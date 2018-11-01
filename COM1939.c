#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <termios.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <limits.h>
#include <sys/time.h>

#include "config.h"
#include "CANInterface.h"

/* jCOM Gateway */
bool bjCOM1939Heartbeat;            /* Will toggle every second                 */

/* COM Port */
int fileCOMPort;                    /* COM port file handle                     */
char sPort[20];                     /* String representation of used port       */

/* Error Management */
bool bCommunicationError;           /* Global error flag                        */
int nErrNum;

bool bErrorOpenCOMPort;             /* True = Error opening COM port            */
bool bErrorCOMPortSettings;         /* True = Error applying COM port settings  */

/* Protocol Functions */
int COM1939_Initialize(char* sCOMPort);     // For instance "/dev/ttyUSB0"
int COM1939_Receive(long* lPGN, int* nPriority, int* nSourceAddress, int* nDestAddress, byte nData[], int* nDataLen);
int COM1939_Transmit(int nPriority, long lPGN, int nSourceAddress, int nDestAddress, byte nData[], int nDataLen);
void COM1939_SetProtocolParameters(byte* nNAME, byte nSA, byte nSABottom, byte nSATop, byte nOpMode, bool bReqRSMessage);
void COM1939_Terminate(void);

/* Gateway management functions */
void COM1939_GetVersion(char* sSWVersion, char* sHWVersion);
void COM1939_ResetGateway(void);
void COM1939_SendMessageMode(byte nMsgMode);
void COM1939_AddFilter(long lPGN);
void COM1939_DelFilter(long lPGN);
void COM1939_RequestStatus(void);
int COM1939_GetStatus(int *nSA);

/* Constants */
#define RS_RXDATA                               4
#define RS_REPSTATUS                            9

#define PGN_RequestMessage                      0x00EA00
#define PGN_GlobalRequestMessage                0x00EAFF

/* Internal functions */
void SendFilterMessage(long lPGN, int fileCOMPort, bool bAdd);
byte ComputeCheckSum(byte pMsg[], int nStart, int nEnd);

// ------------------------------------------------------------------------
// J1939 Initialization
// ------------------------------------------------------------------------
int COM1939_Initialize(char* sCOMPort)
{
    // Initialize the CAN connection
    strcpy(sPort, sCOMPort);
    int nResult = CAN_Initialize(&fileCOMPort, sCOMPort, &bCommunicationError, &nErrNum, &bErrorOpenCOMPort, &bErrorCOMPortSettings);

    // Reset the J1939 converter
    CAN_SendRESETMessage(fileCOMPort);

    // Return the result
    return nResult;

}

// ------------------------------------------------------------------------
// J1939 Protocol Operation
// ------------------------------------------------------------------------
// Returncode: Message return codes according to CANInterface.h
//
int COM1939_Receive(long* lPGN, int* nPriority, int* nSourceAddress, int* nDestAddress, byte nData[], int* nDataLen)
{
    // Declarations
    int nIndex;
    Msg pMessage;

    // Default setting
    *lPGN = 0;
    *nPriority = 0;
    *nSourceAddress = NULLADDRESS;
    *nDestAddress = NULLADDRESS;
    *nDataLen = 0;

    // Get the jCOM1939 heartbeat
    bjCOM1939Heartbeat = bHeartbeat;

    // Check for a received message
    int nMsgType = CAN_Receive(&pMessage, fileCOMPort);

    if(nMsgType == RX_Message)
    {
        // Get the PGN
        *lPGN = ((long)pMessage.Data[RXTX_IDX_PGNMSB]) << 16;
        *lPGN |= ((long)pMessage.Data[RXTX_IDX_PGN2ND]) << 8;
        *lPGN |= ((long)pMessage.Data[RXTX_IDX_PGNLSB]);

        // Get more parameters
        *nPriority = (int)pMessage.Data[RXTX_IDX_PRIORITY];
        *nSourceAddress = (int)pMessage.Data[RXTX_IDX_SRCADDR];
        *nDestAddress = (int)pMessage.Data[RXTX_IDX_DESTADDR];
        *nDataLen = pMessage.DataLen - RXTX_TOTALOVERHEAD;      // Cut off the protocol overhead;

        // Copy the data
        int nPointer = 0;
        for(nIndex = RXTX_IDX_DATASTART; nIndex < pMessage.DataLen; nIndex++)
            nData[nPointer++] = pMessage.Data[nIndex];

    }// end if

    // Return the message type
    return nMsgType;

}

// ------------------------------------------------------------------------
// J1939 Transmit
// ------------------------------------------------------------------------
int COM1939_Transmit(int nPriority, long lPGN, int nSourceAddress, int nDestAddress, byte nData[], int nDataLen)
{
    // Declarations
    int nIndex;
    Msg pMessage;
    int nMsgLen = nDataLen + TOTAL_OVERHEAD;   // Actual message length plus overhead and checksum

    // Fill the TX_1939 message header
    pMessage.Data[RXTX_IDX_MSGSTART] = MSG_TOKEN_START;
    pMessage.Data[RXTX_IDX_MSGID] = MSG_ID_TX;
    pMessage.Data[RXTX_IDX_PGNMSB] = 0;                                     // PGN MSB
    pMessage.Data[RXTX_IDX_PGN2ND] = (byte)((lPGN & (long)0x00FF00) >> 8);  // PGN 2nd byte
    pMessage.Data[RXTX_IDX_PGNLSB] = (byte)(lPGN & (long)0x0000FF);         // PGN LSB
    pMessage.Data[RXTX_IDX_DESTADDR] = (byte)nDestAddress;
    pMessage.Data[RXTX_IDX_SRCADDR] = (byte)nSourceAddress;
    pMessage.Data[RXTX_IDX_MSGLENMSB] = (byte)(nMsgLen >> 8);
    pMessage.Data[RXTX_IDX_MSGLENLSB] = (byte)nMsgLen;
    pMessage.Data[RXTX_IDX_PRIORITY] = (byte)nPriority;

    // Determine the checksum
    // We need the message without stuff bytes to calculate the checksum
    Msg pMsg;
    int nCounter = 0;

    // Copy the protocol overhead
    for(nIndex = 0; nIndex < RXTX_IDX_DATASTART; nIndex++)
    pMsg.Data[nCounter++] = pMessage.Data[nIndex];

    // Copy the actual data without stuff bytes
    for(nIndex = 0; nIndex < nDataLen; nIndex++)
    pMsg.Data[nCounter++] = nData[nIndex];

    // Finally, create the checksum
    byte nChecksum = ComputeCheckSum(pMsg.Data, 1, nCounter - 1);
    pMsg.Data[nCounter] = nChecksum;

    // Fill the TX_1939 message data including byte stuffing
    int nPointer = RXTX_IDX_MSGLENMSB;    // Points to beginning of stuffing range

    for (nIndex = 1; nIndex < nCounter + 1; nIndex++)
    {
          switch (pMsg.Data[nIndex])
          {
              case MSG_TOKEN_START:
                  pMessage.Data[nPointer++] = MSG_TOKEN_ESC;
                  pMessage.Data[nPointer++] = MSG_START_STUFF;
                  break;

              case MSG_TOKEN_ESC:
                  pMessage.Data[nPointer++] = MSG_TOKEN_ESC;
                  pMessage.Data[nPointer++] = MSG_ESC_STUFF;
                  break;

              default:
                  pMessage.Data[nPointer++] = pMsg.Data[nIndex];
                  break;

          }// end switch

    }// end for

    // Process and fill the checksum
    pMessage.DataLen = nPointer;

    // Transmit the message
    return CAN_Transmit(pMessage, fileCOMPort);

}

// ------------------------------------------------------------------------
// J1939 Termination
// ------------------------------------------------------------------------
void COM1939_Terminate()
{
    // Reset the VNA-232
    CAN_SendRESETMessage(fileCOMPort);

    // Close the serial port
    CAN_ClosePort(fileCOMPort);

}

// ------------------------------------------------------------------------
// J1939 Set Protocol Parameters per SET message
// ------------------------------------------------------------------------
void COM1939_SetProtocolParameters(byte* nNAME, byte nSA, byte nSABottom, byte nSATop, byte nOpMode, bool bReqRSMessage)
{
    CAN_SendSETMessage(nNAME, nSA, nSABottom, nSATop, nOpMode, bReqRSMessage, fileCOMPort);

}

// ------------------------------------------------------------------------
// J1939 SendFilterMessage
// ------------------------------------------------------------------------
// Transmits filter message (incl. stuff bytes) according to PGN
//
void SendFilterMessage(long lPGN, int fileCOMPort, bool bAdd)
{
    CAN_SendFilterMessage(lPGN, fileCOMPort, bAdd);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : ComputeCheckSum
// Description : Computes the checksum of a message and inserts it
// -------------------------------------------------------------------------
byte ComputeCheckSum(byte pMsg[], int nStart, int nEnd)
{
    // Declarations
    int nIndex;
    int nCheckSum = 0;
    byte nResult = 0;

    // Create the checksum
    for(nIndex = nStart; nIndex <= nEnd; nIndex++)
        nCheckSum += pMsg[nIndex];
    nCheckSum = ~nCheckSum; // Negation does not work with type byte
    nResult = (byte)nCheckSum;
    nResult += 1;

    return nResult;

}

// Gateway management functions
// ------------------------------------------------------------------------
void COM1939_GetVersion(char* sSoftwareVersion, char* sHardwareVersion)
{
    strcpy(sSoftwareVersion, sSWVersion);
    strcpy(sHardwareVersion, sHWVersion);
}

void COM1939_ResetGateway(void)
{
    // Reset the J1939 converter
    CAN_SendRESETMessage(fileCOMPort);
}

void COM1939_SendMessageMode(byte nMsgMode)
{
    CAN_SendMessageMode(fileCOMPort, nMsgMode);
}

void COM1939_AddFilter(long lPGN)
{
    CAN_SendFilterMessage(lPGN, fileCOMPort, true);
}

void COM1939_DelFilter(long lPGN)
{
    CAN_SendFilterMessage(lPGN, fileCOMPort, false);
}

void COM1939_RequestStatus(void)
{
    CAN_SendRequestMessage(fileCOMPort, MSG_ID_RS);
}

int COM1939_GetStatus(int* nSA)
{
    *nSA = nReportedSourceAddress;
    return nReportedAddrClaimStatus;
}




