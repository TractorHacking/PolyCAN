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

#include "config.h"

/* Function Declarations                                                            */
int CAN_Initialize(int* fileCOMPort, char* sPort, bool* bCommunicationError, int* nErrNum,
                            bool* bErrorOpenCOMPort, bool* bErrorCOMPortSettings);
void CAN_InitializeBuffers(void);
void CAN_ClosePort(int fileCOMPort);
int CAN_Transmit(Msg frame, int fileCOMPort);
int CAN_Transmit1(byte* Data, int DataLen, int fileCOMPort);
int CAN_Receive(Msg* frame, int fileCOMPort);
int CAN_FilterSystemMessage(Msg*);
void CAN_CleanReceiveBuffer(int, int);
void CAN_RemoveStuffBytes(void);
void CAN_ShiftCopyBuffer(int);
byte CAN_ComputeCheckSum(byte*);
int CAN_CreateFilterMessage(byte* pMsg, long lPGN, bool bAdd);
int CAN_SendFilterMessage(long lPGN, int fileCOMPort, bool bAdd);
int CAN_SendSETMessage(byte* nNAME, byte nSA, byte nSABottom, byte nSATop, byte nOpMode, bool bReqRSMessage, int fileCOMPort);
int CAN_CAN_SendRESETMessage(int fileCOMPort);
int CAN_SendRequestMessage(int fileCOMPort, byte cRequestID);
int CAN_SendMessageMode(int fileCOMPort, byte nMsgMode);

/* Global variables                                                                 */
bool bHeartbeat;
char sHWVersion[8];
char sSWVersion[8];
int nErrCntChecksum;
int nErrCntStuffing;

int nReportedAddrClaimStatus;
int nReportedSourceAddress;

byte pCOM_ReceiveBuffer[REC_BUFFER_SIZE];
byte pCOM_CopyBuffer[REC_BUFFER_SIZE];
int nCOM_ReceiveBufferSize = 0;
int nCOM_CopyBufferSize = 0;

/*-FUNCTION-------------------------------------------------------------------
// Routine     : Initialize
// Description : Initializes the CAN hardware interface
// Returncode  : OK / ERROR
// ---------------------------------------------------------------------------
// sCOMPort = "/dev/ttyUSB0" for USB devices
// sCOMPort = "/dev/ttyS0" for RS232 devices
*/
int CAN_Initialize(int* COMPort, char* sCOMPort, bool* bCommunicationError, int* nErrNum, bool* bErrorOpenCOMPort, bool* bErrorCOMPortSettings)
{
    // Initialize buffers
    CAN_InitializeBuffers();

    // Initialize information received from jCOM1939 gateway
    nReportedSourceAddress = NULLADDRESS;
    nReportedAddrClaimStatus = 0;

    strcpy(sHWVersion, "0.00.00");
    strcpy(sSWVersion, "0.00.00");

    nErrCntChecksum = 0;
    nErrCntStuffing = 0;

    // Open the COM port
    int fileCOMPort = open(sCOMPort, O_RDWR | O_NOCTTY | O_NDELAY);
    *COMPort = fileCOMPort;
    if(fileCOMPort == -1)
    {
        *bCommunicationError = true;
        *bErrorOpenCOMPort = true;
        *nErrNum = errno;
        return(ERROR);
    }

    // Configure the COM port
    // -------------------------
    // Get the current settings
    struct termios options;
    if(tcgetattr(fileCOMPort, &options) == -1)
    {
        *bCommunicationError = true;
        *bErrorOpenCOMPort = true;
        *nErrNum = errno;
        return(ERROR);
    }

    options.c_cflag = B115200 | CS8 | CLOCAL | CREAD;
    options.c_iflag = IGNPAR;
    options.c_oflag = 0;
    options.c_lflag = 0;

    options.c_cc[VMIN] = 0; //MIN_MSG_LEN;      // block until n bytes are received
    options.c_cc[VTIME] = 0;               // block until a timer expires (n * 100 mSec.)

    if(tcsetattr(fileCOMPort, TCSANOW, &options) == -1)  // Apply the settings
    {
        *bCommunicationError = true;
        *bErrorCOMPortSettings = true;
        *nErrNum = errno;
        return(ERROR);
    }

    int status;
    if(ioctl(fileCOMPort, TIOCMGET, &status) == -1)
    {
        *bCommunicationError = true;
        *bErrorCOMPortSettings = true;
        *nErrNum = errno;
        return(ERROR);
    }

    status |= TIOCM_DTR;    // turn on DTR
    status |= TIOCM_RTS;    // turn on RTS

    if(ioctl(fileCOMPort, TIOCMSET, &status) == -1)
    {
        *bCommunicationError = true;
        *bErrorCOMPortSettings = true;
        *nErrNum = errno;
        return(ERROR);
    }

    return(OK);

}

//-SUB -----------------------------------------------------------------------
// Routine     : InitializeBuffers
// Description : Initializes COM buffers
// ---------------------------------------------------------------------------
void CAN_InitializeBuffers(void)
{
    nCOM_ReceiveBufferSize = 0;
    nCOM_CopyBufferSize = 0;

    int nIndex;
    for(nIndex = 0; nIndex < REC_BUFFER_SIZE; nIndex++)
    {
        pCOM_ReceiveBuffer[nIndex] = 0;
        pCOM_CopyBuffer[nIndex] = 0;

    }// end for

}

//-SUB -----------------------------------------------------------------------
// Routine     : ClosePort
// Description : Closes the port
// ---------------------------------------------------------------------------
void CAN_ClosePort(int fileCOMPort)
{
    // CLose the COM Port
    close(fileCOMPort);

}

//-SUB------------------------------------------------------------------------
// Routine     : Transmit
// Description : Transmit CAN message
// ---------------------------------------------------------------------------
int CAN_Transmit(Msg frame, int fileCOMPort)
{
     // Send the message
    return write(fileCOMPort, frame.Data, frame.DataLen);

}

//-SUB------------------------------------------------------------------------
// Routine     : Transmit
// Description : Transmit
// ---------------------------------------------------------------------------
int CAN_Transmit1(byte* Data, int DataLen, int fileCOMPort)
{
     // Send the message
    return write(fileCOMPort, Data, DataLen);

}

//-FUNCTION-------------------------------------------------------------------
// Routine     : Receive
// Description : Receive CAN message
// Returncode  : See message return codes in header file
// ---------------------------------------------------------------------------
int CAN_Receive(Msg* frame, int fileCOMPort)
{
    // Declarations
    bool bNewMsg = false;
    int nRetCode = RX_NoMessage;
    int nIndex = 0;
    unsigned char cData[COM_BUFFER_SIZE];

    // Regardless of the current status, read the com port
    // ---------------------------------------------------
    int nBytes = read(fileCOMPort, &cData[0], COM_BUFFER_SIZE);

    // Read the string and attach to global buffer
    for (nIndex = 0; nIndex < nBytes; nIndex++)
    {
        // Prevent buffer overflow
        if(nCOM_ReceiveBufferSize == REC_BUFFER_SIZE - 1)
        {
            // There must be something very serious going on when the
            // buffer overflows. As a protective measure we clear the
            // entire buffer
            nCOM_ReceiveBufferSize = 0;
            return RX_FaultyMessage;

        }// end if

        pCOM_ReceiveBuffer[nCOM_ReceiveBufferSize++] = cData[nIndex];

    }// end for

    // Extract the next message
    // ----------------------------------------------------
    // Find MSG_TOKEN_START
    for (nIndex = 0; nIndex < nCOM_ReceiveBufferSize; nIndex++)
        if (pCOM_ReceiveBuffer[nIndex] == MSG_TOKEN_START)
            break;

    // In case the first byte is NOT MSG_TOKEN_START, clean the buffer
    if (nIndex > 0)
        CAN_CleanReceiveBuffer(0, nIndex);

    // Proceed only when minimum messsage length is available
    if(nCOM_ReceiveBufferSize < MIN_MSG_LEN)
        return RX_NoMessage;

    // Extract some message specifics from the buffer
    int nPointer = 1;   // Points to data length MSB
    int nOffset = 1;
    int nMSB = 0;
    int nLSB = 0;

    // Determine the actual data length MSB
    if (pCOM_ReceiveBuffer[nPointer] == MSG_TOKEN_ESC && pCOM_ReceiveBuffer[nPointer + 1] == MSG_START_STUFF)
    {
        nMSB = MSG_TOKEN_START;
        nOffset = 2;
    }// end if
    else if (pCOM_ReceiveBuffer[nPointer] == MSG_TOKEN_ESC && pCOM_ReceiveBuffer[nPointer + 1] == MSG_ESC_STUFF)
    {
        nMSB = MSG_TOKEN_ESC;
        nOffset = 2;
    }// end else if
    else
    {
        nMSB = pCOM_ReceiveBuffer[nPointer];
        nOffset = 1;
    }// end else

    // Determine the actual data length LSB
    nPointer += nOffset;
    if (pCOM_ReceiveBuffer[nPointer] == MSG_TOKEN_ESC && pCOM_ReceiveBuffer[nPointer + 1] == MSG_START_STUFF)
    {
        nLSB = MSG_TOKEN_START;
        nOffset = 2;
    }// end if
    else if (pCOM_ReceiveBuffer[nPointer] == MSG_TOKEN_ESC && pCOM_ReceiveBuffer[nPointer + 1] == MSG_ESC_STUFF)
    {
        nLSB = MSG_TOKEN_ESC;
        nOffset = 2;
    }// end else if
    else
    {
        nLSB = pCOM_ReceiveBuffer[nPointer];
        nOffset = 1;
    }// end else
    nPointer += nOffset; // nPointer now points to first data byte

    // Determine the actual data length
    int nDataLen = (nMSB << 8) + nLSB;

    // Scan through the buffer to find the end of the message
    nIndex = nPointer;
    int nDataCounter = 0;
    while (nIndex < nCOM_ReceiveBufferSize)
    {
        // Check for another MSG_TOKEN_START
        if (pCOM_ReceiveBuffer[nIndex] == MSG_TOKEN_START)
        {
            bNewMsg = true;
            break;
        }

        // In the following we do not check if the second stuff byte exists.
        // This method helps to detect byte stuffing errors.
        if (pCOM_ReceiveBuffer[nIndex] == MSG_TOKEN_ESC)
            nOffset = 2;
        else if (pCOM_ReceiveBuffer[nIndex] == MSG_TOKEN_ESC)
            nOffset = 2;
        else
            nOffset = 1;

        nIndex += nOffset;
        nDataCounter++;

        if (nDataCounter == nDataLen)
            break;

    }// end while

    // We have a valid message when the counted data matches the reported data
    if (nDataCounter == 0 || nDataCounter != nDataLen)
    {
        // Determine whether this is an incomplete or faulty message
        if(bNewMsg == true)
        {
            // The reported message length does not match the message data,
            // but there is already a new message in the buffer, which
            // indicates a byte stuffing error.
            nRetCode = RX_FaultyMessage;

            // Clean the receive buffer
            CAN_CleanReceiveBuffer(0, nDataCounter + 3); // Include overhead
        }
        else
            nRetCode = RX_NoMessage;

    }// end if
    else
    {
        // nIndex now points to the first byte after the message
        // Copy the entire message
        nCOM_CopyBufferSize = nIndex;
        for (nIndex = 0; nIndex < nCOM_CopyBufferSize; nIndex++)
            pCOM_CopyBuffer[nIndex] = pCOM_ReceiveBuffer[nIndex];

        // Clean the receive buffer
        CAN_CleanReceiveBuffer(0, nCOM_CopyBufferSize);

        // Remove stuffing bytes from copy buffer
        CAN_RemoveStuffBytes();

        // Fill the data into the message frame structure
        nDataLen = nDataLen + 3; // Add overhead length
        frame->DataLen = nDataLen;

        // Copy the data
        for (nIndex = 0; nIndex < nDataLen; nIndex++)
            frame->Data[nIndex] = pCOM_CopyBuffer[nIndex];

        // Verify the checksum
        byte nChecksum = CAN_ComputeCheckSum(frame->Data);
        if(nChecksum != frame->Data[nDataLen - 1])
            nRetCode = RX_FaultyMessage;
        else
            nRetCode = CAN_FilterSystemMessage(frame);

    }// end else

    return nRetCode;

}

//-FUNCTION ----------------------------------------------------------------
// Routine     : CAN_FilterSystemMessage
// Description : System messages such as STATS and ACK should not be
//               passed to the J1939 protocol stack
//               The same applies to empty messages after polling
// Returncode  : OK/NOMSG - NOMSG indicates a system message
// -------------------------------------------------------------------------
// Note: The function will increase the ACK counters for FA and TX
//
int CAN_FilterSystemMessage(Msg* frame)
{
    // Declarations
    int nRetCode = RX_Message;
    char sNumber[5];

    switch (frame->Data[MSG_IDX_ID])
    {
        case MSG_ID_RS:

            nReportedSourceAddress = (int)frame->Data[RS_IDX_SA];
            nReportedAddrClaimStatus = (int)frame->Data[RS_IDX_STATUS];

            nRetCode = RX_RS;
            break;

        case MSG_ID_HEART:
        case MSG_ID_VERSION:

            // Record the heartbeat
            if(frame->Data[MSG_IDX_ID] == MSG_ID_HEART)
                bHeartbeat = !bHeartbeat;

            // Fill the HW version number
            sprintf(sNumber, "%d", frame->Data[4]);
            sHWVersion[0] = sNumber[0];

            sprintf(sNumber, "%d", frame->Data[5]);
            if(strlen(sNumber) == 1)
            {
                sHWVersion[2] = '0';
                sHWVersion[3] = sNumber[0];
            }
            else
            {
                sHWVersion[2] = sNumber[0];
                sHWVersion[3] = sNumber[1];
            }

            sprintf(sNumber, "%d", frame->Data[6]);
            if(strlen(sNumber) == 1)
            {
                sHWVersion[5] = '0';
                sHWVersion[6] = sNumber[0];
            }
            else
            {
                sHWVersion[5] = sNumber[0];
                sHWVersion[6] = sNumber[1];
            }

            // Fill the SW version number
            sprintf(sNumber, "%d", frame->Data[7]);
            sSWVersion[0] = sNumber[0];

            sprintf(sNumber, "%d", frame->Data[8]);
            if(strlen(sNumber) == 1)
            {
                sSWVersion[2] = '0';
                sSWVersion[3] = sNumber[0];
            }
            else
            {
                sSWVersion[2] = sNumber[0];
                sSWVersion[3] = sNumber[1];
            }

            sprintf(sNumber, "%d", frame->Data[9]);
            if(strlen(sNumber) == 1)
            {
                sSWVersion[5] = '0';
                sSWVersion[6] = sNumber[0];
            }
            else
            {
                sSWVersion[5] = sNumber[0];
                sSWVersion[6] = sNumber[1];
            }

            if(frame->Data[MSG_IDX_ID] == MSG_ID_HEART)
                nRetCode = RX_HEART;
            else
                nRetCode = RX_VERSION;

            break;

        case MSG_ID_ACK:

            switch(frame->Data[MSG_IDX_ACK_MSG])
            {
                case MSG_ID_FA:
                    nRetCode = RX_ACK_FA;
                    break;

                case MSG_ID_FD:
                    nRetCode = RX_ACK_FD;
                    break;

                case MSG_ID_TX:
                    nRetCode = RX_ACK_TX;
                    break;

                case MSG_ID_RESET:
                    nRetCode = RX_ACK_RESET;
                    break;

                case MSG_ID_SETPARAM:
                    nRetCode = RX_ACK_SETPARAM;
                    break;

                case MSG_ID_SETPARAM1:
                    nRetCode = RX_ACK_SETPARAM1;
                    break;

                case MSG_ID_SETMSGMODE:
                    nRetCode = RX_ACK_MSGMODE;
                    break;

                case MSG_ID_TXL:
                    nRetCode = RX_ACK_TXL;
                    break;

                case MSG_ID_SETACK:
                    nRetCode = RX_ACK_SETACK;
                    break;

                case MSG_ID_SETHEART:
                    nRetCode = RX_ACK_SETHEART;
                    break;

                case MSG_ID_FLASH:
                    nRetCode = RX_ACK_FLASH;
                    break;

            }// end switch

            break;

    }// end switch

    // Return the result
    return nRetCode;

}

//-SUB----------------------------------------------------------------------
// Routine     : CAN_CleanReceiveBuffer
// Description : Remove current messages from global receive buffer
// -------------------------------------------------------------------------
void CAN_CleanReceiveBuffer(int nStart, int nLen)
{
    // Any leading bytes in the buffer must be trash
    nLen += nStart;
    int nSource = nLen;
    int nDest = 0;

    nCOM_ReceiveBufferSize -= nLen;

    int nIndex;
    for(nIndex = 0; nIndex < nCOM_ReceiveBufferSize; nIndex++)
        pCOM_ReceiveBuffer[nDest++] = pCOM_ReceiveBuffer[nSource++];

}

//-SUB----------------------------------------------------------------------
// Routine     : CAN_RemoveStuffBytes
// Description : Remove stuff bytes from copy buffer
// -------------------------------------------------------------------------
void CAN_RemoveStuffBytes(void)
{
    // Scan through the global receive buffer
    int nIndex;
    for(nIndex = 0; nIndex < nCOM_CopyBufferSize; nIndex++)
    {
        if (nCOM_CopyBufferSize - nIndex >= 2)
        {
            if (pCOM_CopyBuffer[nIndex] == MSG_TOKEN_ESC
            && pCOM_CopyBuffer[nIndex + 1] == MSG_START_STUFF)
            {
                pCOM_CopyBuffer[nIndex] = MSG_TOKEN_START;
                CAN_ShiftCopyBuffer(nIndex + 1);
            }// end if
            else if (pCOM_CopyBuffer[nIndex] == MSG_TOKEN_ESC
                    && pCOM_CopyBuffer[nIndex + 1] == MSG_ESC_STUFF)
            {
                pCOM_CopyBuffer[nIndex] = MSG_TOKEN_ESC;
                CAN_ShiftCopyBuffer(nIndex + 1);
            }// end else

        } // end if

    }// end for

}

//-SUB----------------------------------------------------------------------
// Routine     : CAN_ShiftCopyBuffer
// Description : Removes byte in receive buffer
// -------------------------------------------------------------------------
void CAN_ShiftCopyBuffer(int nPos)
{
    // Any leading bytes in the buffer must be trash
    int nSource = nPos + 1;
    int nDest = nPos;

    int nIndex;
    for(nIndex = 0; nIndex < nCOM_CopyBufferSize - nPos - 1; nIndex++)
        pCOM_CopyBuffer[nDest++] = pCOM_CopyBuffer[nSource++];

    nCOM_CopyBufferSize -= 1;

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : CAN_ComputeCheckSum
// Description : Computes the checksum of a message and inserts it
// -------------------------------------------------------------------------
byte CAN_ComputeCheckSum(byte* pMsg)
{
    // Declarations
    byte nCheckSum = 0;

    // Checksum range (Data Field + MSB + LSB - Checksum Field)
    int nLen = ((int)pMsg[RXTX_IDX_MSGLENMSB] << 8);
    nLen += (int)pMsg[RXTX_IDX_MSGLENLSB] + 1;

    // Create the checksum
    int nIndex;
    for(nIndex = 1; nIndex <= nLen; nIndex++)
        nCheckSum += pMsg[nIndex];

    return (byte)((~(int)nCheckSum) + 1);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : CAN_CreateFilterMessage
// Description : Creates filter message (incl. stuff bytes) according to PGN
// Returncode  : Total message length incl. stuff bytes
// -------------------------------------------------------------------------
int CAN_CreateFilterMessage(byte* pMsg, long lPGN, bool bAdd)
{
    // Declarations
    int nTotalMsgLen = 0;
    int nMsgLen = 0;
    int nMsgID = 0;

    if(bAdd == true)
    {
        nMsgLen = MSG_LEN_FA;
        nTotalMsgLen = nMsgLen + MSG_OVERHEAD;    // Initial total message length without stuff bytes
        nMsgID = MSG_ID_FA;

    }// end if
    else
    {
        nMsgLen = MSG_LEN_FD;
        nTotalMsgLen = nMsgLen + MSG_OVERHEAD;
        nMsgID = MSG_ID_FD;

    }// end else

    byte nPGN_MSB = (byte)(lPGN >> 16);
    byte nPGN_2ND = (byte)((lPGN & (long)0x00FF00) >> 8);
    byte nPGN_LSB = (byte)(lPGN & (long)0x0000FF);

    // Check for need of stuff bytes
    if (nPGN_MSB == MSG_TOKEN_START || nPGN_MSB == MSG_TOKEN_ESC)
        nTotalMsgLen++;
    if (nPGN_2ND == MSG_TOKEN_START || nPGN_2ND == MSG_TOKEN_ESC)
        nTotalMsgLen++;
    if (nPGN_LSB == MSG_TOKEN_START || nPGN_LSB == MSG_TOKEN_ESC)
        nTotalMsgLen++;

    // Create the message without stuff bytes and checksum
    byte pMsgCopy[nMsgLen + MSG_OVERHEAD];

    pMsgCopy[0] = MSG_TOKEN_START;
    pMsgCopy[1] = 0;                // Length MSB
    pMsgCopy[2] = (byte)nMsgLen;    // Length LSB
    pMsgCopy[3] = (byte)nMsgID;     // FA message ID
    pMsgCopy[4] = nPGN_MSB;         // PGN
    pMsgCopy[5] = nPGN_2ND;
    pMsgCopy[6] = nPGN_LSB;

    // Create the checksum
    pMsgCopy[FAFD_IDX_CHKSUM] = CAN_ComputeCheckSum(pMsgCopy);

    if (pMsgCopy[FAFD_IDX_CHKSUM] == MSG_TOKEN_START || pMsgCopy[FAFD_IDX_CHKSUM] == MSG_TOKEN_ESC)
        nTotalMsgLen++;

    // Fill all information incl. stuff bytes
    pMsg[0] = MSG_TOKEN_START;

    int nPointer = 1;
    int nIndex;
    for(nIndex = 1; nIndex < nMsgLen + MSG_OVERHEAD; nIndex++)
    {
        if (pMsgCopy[nIndex] == MSG_TOKEN_START)
        {
            pMsg[nPointer++] = MSG_TOKEN_ESC;
            pMsg[nPointer++] = MSG_START_STUFF;
        }//end if
        else if (pMsgCopy[nIndex] == MSG_TOKEN_ESC)
        {
            pMsg[nPointer++] = MSG_TOKEN_ESC;
            pMsg[nPointer++] = MSG_ESC_STUFF;
        }// end else if
        else
            pMsg[nPointer++] = pMsgCopy[nIndex];

    }// end for

    // Return the total message length
    return nTotalMsgLen;

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : SendFilterMessage
// Description : Transmits filter message (incl. stuff bytes) according to PGN
// Returncode  : 0 = OK, 1 = Transmit Error
// -------------------------------------------------------------------------
// bAdd = true => Add filter
// bAdd = false => Delete filter
//
int CAN_SendFilterMessage(long lPGN, int fileCOMPort, bool bAdd)
{
    // Declarations
    Msg pMessage;

    // Create the filter message
    pMessage.DataLen = CAN_CreateFilterMessage(pMessage.Data, lPGN, bAdd);

    // Transmit the message
    return CAN_Transmit(pMessage, fileCOMPort);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : SendSETMessage
// Description : Transmits SET message
// Returncode  : 0 = OK, 1 = Transmit Error
// -------------------------------------------------------------------------
int CAN_SendSETMessage(byte* nNAME, byte nSA, byte nSABottom, byte nSATop,
                                 byte nOpMode, bool bReqRSMessage, int fileCOMPort)
{
    // Declarations
    byte pMsg[50];
    int nMsgLen = MSG_LEN_SET + MSG_OVERHEAD;    // Initial total message length without stuff bytes

    // Check for need of stuff bytes
    int nIndex;
    for(nIndex = 0; nIndex < 8; nIndex++)
        if (nNAME[nIndex] == MSG_TOKEN_START || nNAME[nIndex] == MSG_TOKEN_ESC)
            nMsgLen++;

    if(nSA == MSG_TOKEN_START || nSA == MSG_TOKEN_ESC)
        nMsgLen++;
    if(nSABottom == MSG_TOKEN_START || nSABottom == MSG_TOKEN_ESC)
        nMsgLen++;
    if(nSATop == MSG_TOKEN_START || nSATop == MSG_TOKEN_ESC)
        nMsgLen++;

    // Create the message without stuff bytes and checksum
    byte pMsgCopy[MSG_LEN_SET + MSG_OVERHEAD];

    pMsgCopy[0] = MSG_TOKEN_START;
    pMsgCopy[1] = 0;                    // Length MSB
    pMsgCopy[2] = MSG_LEN_SET;          // Length LSB

    // Set the message ID
    if(bReqRSMessage == true)
        pMsgCopy[3] = MSG_ID_SETPARAM1;
    else
        pMsgCopy[3] = MSG_ID_SETPARAM;

    for(nIndex = 0; nIndex < 8; nIndex++)
        pMsgCopy[nIndex + SET_IDX_NAME] = nNAME[nIndex];

    pMsgCopy[SET_IDX_SA] = nSA;
    pMsgCopy[SET_IDX_ADDRRANGE_BOTTOM] = nSABottom;
    pMsgCopy[SET_IDX_ADDRRANGE_TOP] = nSATop;
    pMsgCopy[SET_IDX_OPMODE] = nOpMode;

    // Create the checksum
    pMsgCopy[SET_IDX_OPMODE+1] = CAN_ComputeCheckSum(pMsgCopy);

    if (pMsgCopy[SET_IDX_OPMODE+1] == MSG_TOKEN_START || pMsgCopy[SET_IDX_OPMODE+1] == MSG_TOKEN_ESC)
        nMsgLen++;

    // Fill all information incl. stuff bytes
    pMsg[0] = MSG_TOKEN_START;

    int nPointer = 1;
    for(nIndex = 1; nIndex < MSG_LEN_SET + MSG_OVERHEAD; nIndex++)
    {
        if (pMsgCopy[nIndex] == MSG_TOKEN_START)
        {
            pMsg[nPointer++] = MSG_TOKEN_ESC;
            pMsg[nPointer++] = MSG_START_STUFF;
        }//end if
        else if (pMsgCopy[nIndex] == MSG_TOKEN_ESC)
        {
            pMsg[nPointer++] = MSG_TOKEN_ESC;
            pMsg[nPointer++] = MSG_ESC_STUFF;
        }// end else if
        else
            pMsg[nPointer++] = pMsgCopy[nIndex];

    }// end for

    return CAN_Transmit1(pMsg, nMsgLen, fileCOMPort);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : SendRESETMessage
// Description : Transmits RESET message
// Returncode  : 0 = OK, 1 = Transmit Error
// -------------------------------------------------------------------------
int CAN_SendRESETMessage(int fileCOMPort)
{
    // Declarations
    int nMsgLen = MSG_LEN_RESET + MSG_OVERHEAD;
    byte msg_RESET[] = { MSG_TOKEN_START, MSG_LEN_MSB, MSG_LEN_RESET, MSG_ID_RESET, RESET_UNLOCK_KEY1, RESET_UNLOCK_KEY2, RESET_UNLOCK_KEY3, 0x00, 0x00 };

    // Create the checksum
    msg_RESET[RESET_IDX_ULKEY3 + 1] = CAN_ComputeCheckSum(msg_RESET);

    // Check if checksum is START or ESC token
    if(msg_RESET[RESET_IDX_ULKEY3 + 1] == MSG_TOKEN_START)
    {
        msg_RESET[RESET_IDX_ULKEY3 + 1] = MSG_TOKEN_ESC;
        msg_RESET[RESET_IDX_ULKEY3 + 2] = MSG_START_STUFF;
        nMsgLen++;
    }
    else if (msg_RESET[RESET_IDX_ULKEY3 + 1] == MSG_TOKEN_ESC)
    {
        msg_RESET[RESET_IDX_ULKEY3 + 1] = MSG_TOKEN_ESC;
        msg_RESET[RESET_IDX_ULKEY3 + 2] = MSG_ESC_STUFF;
        nMsgLen++;
    }

    // Transmit the message
    return CAN_Transmit1(msg_RESET, nMsgLen, fileCOMPort);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : SendMessageMode
// Description : Transmits message mode
// Returncode  : 0 = OK, 1 = Transmit Error
// -------------------------------------------------------------------------
int CAN_SendMessageMode(int fileCOMPort, byte nMsgMode)
{
    // Declarations
    int nMsgLen = MSG_LEN_MM + MSG_OVERHEAD;
    byte msg_MESSAGEMODE[] = { MSG_TOKEN_START, MSG_LEN_MSB, MSG_LEN_MM, MSG_ID_SETMSGMODE, 0x00, 0x00, 0x00 };

    // Store the message mode
    msg_MESSAGEMODE[nMsgLen - 2] = nMsgMode;

    // Create the checksum
    msg_MESSAGEMODE[nMsgLen - 1] = CAN_ComputeCheckSum(msg_MESSAGEMODE);

    // Check if checksum is START or ESC token
    if(msg_MESSAGEMODE[nMsgLen - 1] == MSG_TOKEN_START)
    {
        msg_MESSAGEMODE[nMsgLen - 1] = MSG_TOKEN_ESC;
        msg_MESSAGEMODE[nMsgLen] = MSG_START_STUFF;
        nMsgLen++;
    }
    else if (msg_MESSAGEMODE[nMsgLen - 1] == MSG_TOKEN_ESC)
    {
        msg_MESSAGEMODE[nMsgLen - 1] = MSG_TOKEN_ESC;
        msg_MESSAGEMODE[nMsgLen] = MSG_ESC_STUFF;
        nMsgLen++;
    }

    // Transmit the message
    return CAN_Transmit1(msg_MESSAGEMODE, nMsgLen, fileCOMPort);

}

//-FUNCTION-----------------------------------------------------------------
// Routine     : SendRequestMessage
// Description : Transmits REQUEST message
// Returncode  : 0 = OK, 1 = Transmit Error
// -------------------------------------------------------------------------
int CAN_SendRequestMessage(int fileCOMPort, byte cRequestID)
{
    // Declarations
    int nMsgLen = MSG_LEN_RQ + MSG_OVERHEAD;
    byte msg_RQ[] = { MSG_TOKEN_START, MSG_LEN_MSB, MSG_LEN_RQ, MSG_ID_RQ, MSG_ID_RX, 0x00, 0x00 };

    // Fill the request ID
    msg_RQ[RQ_IDX_REQUESTED] = cRequestID;

    // Create the checksum
    msg_RQ[RQ_IDX_REQUESTED + 1] = CAN_ComputeCheckSum(msg_RQ);

    if(msg_RQ[RQ_IDX_REQUESTED + 1] == MSG_TOKEN_START)
    {
        msg_RQ[RQ_IDX_REQUESTED + 1] = MSG_TOKEN_ESC;
        msg_RQ[RQ_IDX_REQUESTED + 2] = MSG_START_STUFF;
        nMsgLen++;
    }
    else if (msg_RQ[RQ_IDX_REQUESTED + 1] == MSG_TOKEN_ESC)
    {
        msg_RQ[RQ_IDX_REQUESTED + 1] = MSG_TOKEN_ESC;
        msg_RQ[RQ_IDX_REQUESTED + 2] = MSG_ESC_STUFF;
        nMsgLen++;
    }

    // Transmit the message
    return CAN_Transmit1(msg_RQ, nMsgLen, fileCOMPort);

}


