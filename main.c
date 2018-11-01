#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>

#include "config.h"
#include "CANInterface.h"
#include "COM1939.h"

byte msgNAME[] =
{
   (byte)(NAME_IDENTITY_NUMBER & 0xFF),
   (byte)((NAME_IDENTITY_NUMBER >> 8) & 0xFF),
   (byte)(((NAME_MANUFACTURER_CODE << 5) & 0xFF) | (NAME_IDENTITY_NUMBER >> 16)),
   (byte)(NAME_MANUFACTURER_CODE >> 3),
   (byte)((NAME_FUNCTION_INSTANCE << 3) | NAME_ECU_INSTANCE),
   (byte)(NAME_FUNCTION),
   (byte)(NAME_VEHICLE_SYSTEM << 1),
   (byte)((NAME_ARBITRARY_ADDRESS_CAPABLE << 7) | (NAME_INDUSTRY_GROUP << 4) | (NAME_VEHICLE_SYSTEM_INSTANCE))
};

byte SampleTxData[] = {0x38, 0x37, 0x36, 0x35, 0x34, 0x33, 0x32, 0x31};

// Function calls in this module
int kbhit(char* key);

int main(int argc, char * argv[]){
   // Declarations
   char sCOMPort[20];
   int nIndex;
   int nSA;
   int nJ1939Status;

   long lPGN;
   int nPriority;
   int nSourceAddress;
   int nDestAddress;
   int nDataLen;
   byte nData[MAXDATALEN];

   char sSWVersion[10];
   char sHWVersion[10];
   char* fileName;
   struct timeval start,current;
   FILE* outFile;

   // Initialize the port and protocol settings
   strcpy(sCOMPort, COMPORT);
   COM1939_Initialize(&sCOMPort[0]);
   COM1939_SendMessageMode(MSGMODE_GATEWAY2);

   if(bCommunicationError == false)
   {
   printf("COM Port Init OK. %s\n\r", sPort);
   printf("Press 'h' for Help\n\r");
   }// end if
   else if(bErrorOpenCOMPort == true){
      fprintf(stderr,"Unable to open COM port: %s - ErrNo: %d\n\rDid you run as super user?\n\r", sPort, nErrNum);
      perror(NULL);
      exit(EXIT_FAILURE);
   }
   else if(bErrorCOMPortSettings == true){
      fprintf(stderr,"Unable to apply COM port settings: %s - ErrNo: %d\n\rDid you run as super user?\n\r", sPort, nErrNum);
      perror(NULL);
      exit(EXIT_FAILURE);
   }


   if(argc != 1){//grab the desired outputfile from the first argument
      fileName = argv[1];
   }
   else{
      time_t t = time(NULL);
      struct tm tm = *(localtime(&t));
      fileName = malloc(40);
      sprintf(fileName,"logs/outLog-%02d-%02d--%02d.%02d",\
            tm.tm_mon+1,tm.tm_mday,(tm.tm_hour>12)?tm.tm_hour-12:tm.tm_hour,tm.tm_min);
   }
   outFile = fopen(fileName,"w+");
   //outFile = fopen(fileName,O_TRUNC|O_WRONLY|O_CREAT,S_IRUSR|S_IWUSR);
   if(outFile==NULL){
      perror(NULL);
      exit(EXIT_FAILURE);
   }

   gettimeofday(&start,NULL);
   // Main loop
   bool bExit = false;
   bool bAllowAllPGNs = false;
   bool bEnableHeartbeat = false;
   while(1)
   {
   // Wait for assigned system loop time period
   usleep(SYSTEM_LOOP_TIME);

   // Call the COM1939 protocol stack
   int nStatus = COM1939_Receive(&lPGN, &nPriority, &nSourceAddress, &nDestAddress, &nData[0], &nDataLen);
   gettimeofday(&current,NULL);

   switch(nStatus)
   {
      case RX_Message:        // PGN received
            printf("+%03d.%06d::PGN:%ld P:%d SA:%d DA:%d Len:%d Data:",(int)(current.tv_sec - start.tv_sec),(int)(current.tv_usec - start.tv_usec), lPGN, nPriority, nSourceAddress, nDestAddress, nDataLen);
            fprintf(outFile,"+%03d.%06d::PGN:%ld P:%d SA:%d DA:%d Len:%d Data:",(int)(current.tv_sec - start.tv_sec),(int)(current.tv_usec - start.tv_usec), lPGN, nPriority, nSourceAddress, nDestAddress, nDataLen);
            for(nIndex = 0; nIndex < nDataLen; nIndex++){
               printf("%x ", nData[nIndex]);
               fprintf(outFile,"%x ", nData[nIndex]);
            }
            printf("\n\r");
            fprintf(outFile,"\n\r");
            break;

      case RX_ACK_FA:
            printf(" FA ACK\n\r");
            break;

      case RX_ACK_FD:
            printf(" FD ACK\n\r");
            break;

      case RX_ACK_SETPARAM:
            printf(" SETPARAM ACK\n\r");
            break;

      case RX_ACK_SETPARAM1:
            printf(" SETPARAM1 ACK\n\r");
            break;

      case RX_ACK_RESET:
            printf(" RESET ACK\n\r");
            break;

      case RX_ACK_MSGMODE:
            printf(" SETMSGMODE ACK\n\r");
            break;

      case RX_HEART:
            if(bEnableHeartbeat == true)
            {
               if(bjCOM1939Heartbeat == true)
                  printf("Tick\n\r");
               else
                  printf("Tock\n\r");
            }
            break;

      case RX_RS:
            nJ1939Status = COM1939_GetStatus(&nSA);
            printf(" Status: \n\r");
            printf("SA: %d - ", nSA );

            switch(nJ1939Status)
            {
               case RS_STATUS_NONE:
                  printf("No J1939 Address Claimed.\n\r");
                  break;

               case RS_STATUS_ADDRESSCLAIMINPROGRESS:
                  printf("Address Claim in Progress.\n\r");
                  break;

               case RS_STATUS_ADRESSCLAIMSUCCESSFUL:
                  printf("Address Claim Successful.\n\r");
                  break;

               case RS_STATUS_ADDRESSCLAIMFAILED:
                  printf("Address Claim Failed.\n\r");
                  break;

               case RS_STATUS_LISTENONLYMODE:
                  printf("Listen-Only Mode.\n\r");
                  break;

            }// end switch

            break;

   }// end switch

   // Check for user interaction
   char key;
   if(kbhit(&key))
   {
      switch(key)
      {
            case 'a':       // Allow all messages (Toggle)
               bAllowAllPGNs = !bAllowAllPGNs;
               if(bAllowAllPGNs == true)
                  COM1939_AddFilter(PGN_ALLOW_ALL);
               else
                  COM1939_DelFilter(PGN_ALLOW_ALL);
               break;

            case 'b':
               bEnableHeartbeat = !bEnableHeartbeat;
               break;

            case 'c':
               COM1939_SetProtocolParameters(msgNAME, SA_PREFERRED, ADDRESSRANGEBOTTOM, ADDRESSRANGETOP, OPMODE_EVENT, true);
               break;

            case 'd':
               COM1939_DelFilter(PGN_SAMPLE_RX);
               break;

            case 'f':
               COM1939_AddFilter(PGN_SAMPLE_RX);
               break;

            case 'h':       // Help message
               printf("\n\ra - Toggle Pass [a]ll PGNs");
               printf("\n\rb - Toggle heart[b]eat");
               printf("\n\rc - [c]laim address");
               printf("\n\rd - [d]elete sample PGN filter");
               printf("\n\rf - Add sample PGN [f]ilter");
               printf("\n\rr - Reset gateway");
               printf("\n\rs - Request J1939 [s]tatus");
               printf("\n\rt - [t]ransmit sample PGN");
               printf("\n\rv - Get hardware & software [v]ersion");
               printf("\n\rx - E[x]it\n\r");
               break;

            case 'r':
               COM1939_ResetGateway();
               COM1939_SendMessageMode(MSGMODE_GATEWAY2);
               break;

            case 's':
               COM1939_RequestStatus();
               break;

            case 't':
               nJ1939Status = COM1939_GetStatus(&nSA);

               if(nJ1939Status == RS_STATUS_ADRESSCLAIMSUCCESSFUL)
               {
                  // Transmit the sample data
                  COM1939_Transmit(6, PGN_SAMPLE_TX, nSA, DEST_ADDR_SAMPLE, &SampleTxData[0], 8);
                  printf("Transmitted PGN %ld to node #%d:\n\r", (long)PGN_SAMPLE_TX, DEST_ADDR_SAMPLE);
                  for(nIndex = 0; nIndex < 8; nIndex++)
                        printf("0x%x ", SampleTxData[nIndex]);
                  printf("\n\r");

               }// end if
               else
               {
                  // Print an error message
                  printf("Unable to Transmit - Reason: ");

                  switch(nJ1939Status)
                  {
                        case RS_STATUS_NONE:
                           printf("No J1939 Address Claimed.\n\r");
                           break;

                        case RS_STATUS_ADDRESSCLAIMINPROGRESS:
                           printf("Address Claim in Progress.\n\r");
                           break;

                        case RS_STATUS_ADDRESSCLAIMFAILED:
                           printf("Address Claim Failed.\n\r");
                           break;

                        case RS_STATUS_LISTENONLYMODE:
                           printf("Listen-Only Mode.\n\r");
                           break;

                  }// end switch

               }// end else

               break;

            case 'v':       // Get version strings
               COM1939_GetVersion(&sSWVersion[0], &sHWVersion[0]);
               printf(" SW: %s HW: %s\n\r", sSWVersion, sHWVersion);
               break;

            case 'x':       // Exit the program
               COM1939_Terminate();
               bExit = true;
               break;

      }// end switch

   }// end if

   if(bExit == true)
      break;

   }// end while

   return 0;

   }// end main

//-FUNCTION-----------------------------------------------------------------
// Routine     : kbhit
// Description : Checks for keyboard input and fetches the code
// Returncode  : OK/ERROR
// -------------------------------------------------------------------------
int kbhit(char* key)
{
   struct termios oldt;
   struct termios newt;
   int ch;
   int oldf;

   tcgetattr(STDIN_FILENO, &oldt);
   newt = oldt;
   newt.c_lflag &= ~(ICANON | ECHO);
   tcsetattr(STDIN_FILENO, TCSANOW, &newt);
      oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
      fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);

      ch = getchar();
      *key = (char)ch;

      tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
      fcntl(STDIN_FILENO, F_SETFL, oldf);

      if(ch != EOF)
      {
         //ungetc(ch, stdin);
         return ERROR;
      }

      return OK;

   }// end kbhit

