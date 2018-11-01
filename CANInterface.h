#ifndef CANEXTERNALS_H_INCLUDED
#define CANEXTERNALS_H_INCLUDED

extern int CAN_Initialize(int* fileCOMPort, char* sPort, bool* bCommunicationError, int* nErrNum, bool* bErrorOpenCOMPort, bool* bErrorCOMPortSettings);
extern void CAN_InitializeBuffers(void);
extern void CAN_ClosePort(int fileCOMPort);
extern int CAN_Transmit(Msg frame, int fileCOMPort);
extern int CAN_Transmit1(byte* Data, int DataLen, int fileCOMPort);
extern int CAN_Receive(Msg* frame, int fileCOMPort);
extern int CAN_FilterSystemMessage(Msg*);
extern void CAN_CleanReceiveBuffer(int, int);
extern void CAN_RemoveStuffBytes(void);
extern void CAN_ShiftCopyBuffer(int);
extern byte CAN_ComputeCheckSum(byte*);
extern int CAN_CreateFilterMessage(byte* pMsg, long lPGN, bool bAdd);
extern int CAN_SendFilterMessage(long lPGN, int fileCOMPort, bool bAdd);
extern int CAN_SendSETMessage(byte* nNAME, byte nSA, byte nSABottom, byte nSATop, byte nOpMode, bool bReqRSMessage, int fileCOMPort);
extern int CAN_SendRESETMessage(int fileCOMPort);
extern int CAN_SendRequestMessage(int fileCOMPort, byte cRequestID);
extern int CAN_SendMessageMode(int fileCOMPort, byte nMsgMode);

extern bool bHeartbeat;
extern char sHWVersion[];
extern char sSWVersion[];
extern int nErrCntChecksum;
extern int nErrCntStuffing;

extern int nReportedAddrClaimStatus;
extern int nReportedSourceAddress;

#endif
