#ifndef COM1939_H
#define COM1939_H

/* jCOM Gateway */
extern bool bjCOM1939Heartbeat;            /* Will toggle every second                 */

/* COM Port */
extern int fileCOMPort;                    /* COM port file handle                     */
extern char sPort[20];                     /* String representation of used port       */

/* Error Management */
extern bool bCommunicationError;           /* Global error flag                        */
extern int nErrNum;

extern bool bErrorOpenCOMPort;             /* True = Error opening COM port            */
extern bool bErrorCOMPortSettings;         /* True = Error applying COM port settings  */

/* Protocol Functions */
extern int COM1939_Initialize(char* sCOMPort);     // For instance "/dev/ttyUSB0"
extern int COM1939_Receive(long* lPGN, int* nPriority, int* nSourceAddress, int* nDestAddress, byte nData[], int* nDataLen);
extern int COM1939_Transmit(int nPriority, long lPGN, int nSourceAddress, int nDestAddress, byte nData[], int nDataLen);
extern void COM1939_SetProtocolParameters(byte* nNAME, byte nSA, byte nSABottom, byte nSATop, byte nOpMode, bool bReqRSMessage);
extern void COM1939_Terminate(void);

/* Gateway management functions */
extern void COM1939_GetVersion(char* sSWVersion, char* sHWVersion);
extern void COM1939_ResetGateway(void);
extern void COM1939_SendMessageMode(byte nMsgMode);
extern void COM1939_AddFilter(long lPGN);
extern void COM1939_DelFilter(long lPGN);
extern void COM1939_RequestStatus(void);
extern int COM1939_GetStatus(int *nSA);

#endif
