#ifndef CONFIG_H_INCLUDED
#define CONFIG_H_INCLUDED

/* User application settings ------------------------------------------------------ */
/* -------------------------------------------------------------------------------- */
#define COMPORT                         "/dev/ttyUSB0"  /* Serial Port              */
//#define COMPORT				"/dev/ttyAMA0"

#define PGN_SAMPLE_RX                   65280           /* Receive PGN              */
#define PGN_SAMPLE_TX                   65281           /* Transmit PGN             */
#define DEST_ADDR_SAMPLE                128             /* Dest Addr for Tx PGN     */

/* J1939 NAME Default settings                                                      */
#define NAME_IDENTITY_NUMBER            0x1FFFFF        /* 21 bits                  */
#define NAME_MANUFACTURER_CODE          0x7FF           /* 11 bits                  */
#define NAME_FUNCTION_INSTANCE          1               /* 5 bits                   */
#define NAME_ECU_INSTANCE               1               /* 3 bits                   */
#define NAME_FUNCTION                   0xFF            /* 8 bits                   */
#define NAME_RESERVED                   0               /* 1 bit                    */
#define NAME_VEHICLE_SYSTEM             0x7F            /* 7 bits                   */
#define NAME_VEHICLE_SYSTEM_INSTANCE    16              /* 4 bits                   */
#define NAME_INDUSTRY_GROUP             0x01            /* 3 bits                   */
#define NAME_ARBITRARY_ADDRESS_CAPABLE  0x01            /* 1 bit                    */

/* J1939 Node Address Settings                                                      */
#define SA_PREFERRED                    150             /* Preferred node address   */
#define ADDRESSRANGEBOTTOM              128             /* Address range low        */
#define ADDRESSRANGETOP                 247             /* Address range high       */

/* System Settings ---------------------------------------------------------------- */
/* -------------------------------------------------------------------------------- */
#define OK                              0
#define ERROR                           1

#define byte                            unsigned char
#define bool                            unsigned char
#define true                            1
#define false                           0

#define SYSTEM_LOOP_TIME                1000             /* microseconds            */

/* COM Port Settings                                                                */
#define REC_BUFFER_SIZE                 2048            /* Applies to the receive buffer
                                                           The maximum J1939 message length = 255 x 7 = 1785
                                                           This buffer size provides sufficient space for stuff bytes */
#define COM_BUFFER_SIZE                 256
#define READ_TIMEOUT                    500
#define WRITE_TIMEOUT                   500
#define REC_BUFFER_FILLTIME             80

/* Gateway operation mode                                                           */
#define OPMODE_LISTENONLY               0
#define OPMODE_EVENT                    1

#define MSGMODE_ECU                     0
#define MSGMODE_GATEWAY1                1
#define MSGMODE_GATEWAY2                2

/* J1939 Message Buffers                                                            */
#define MAXDATALEN                      1785
#define APPMSGBUFFERSIZE                20
#define PGN_ALLOW_ALL                   0x100000

/* J1939 Settings                                                                   */
#define NULLADDRESS                     254
#define GLOBALADDRESS                   255

/* Address Claim Status as received from the jCOM gateway                           */
#define RS_STATUS_NONE                  0
#define RS_STATUS_ADDRESSCLAIMINPROGRESS 1
#define RS_STATUS_ADRESSCLAIMSUCCESSFUL 2
#define RS_STATUS_ADDRESSCLAIMFAILED    3
#define RS_STATUS_LISTENONLYMODE        4

/* Message return codes                                                             */
#define RX_Message                          0
#define RX_NoMessage                        1
#define RX_FaultyMessage                    2
#define RX_HEART                            3
#define RX_ACK_FA                           4
#define RX_ACK_FD                           5
#define RX_ACK_TX                           6
#define RX_ACK_RESET                        7
#define RX_ACK_SETPARAM                     8
#define RX_ACK_SETPARAM1                    9
#define RX_RS                               10
#define RX_ACK_MSGMODE                      11
#define RX_ACK_TXL                          12
#define RX_VERSION                          13
#define RX_ACK_SETACK                       14
#define RX_ACK_SETHEART                     15
#define RX_ACK_FLASH                        16

/* Message Format                                                                   */
#define MSG_TOKEN_START                     192
#define MSG_TOKEN_ESC                       219
#define MSG_START_STUFF                     220
#define MSG_ESC_STUFF                       221

#define MSG_OVERHEAD                        3
#define TOTAL_OVERHEAD                      8
#define RXTX_TOTALOVERHEAD                  11

#define MIN_MSG_LEN                         6

/* Message field indexes                                                            */
#define MSG_IDX_ID                          3
#define MSG_IDX_ACK_MSG                     4

#define FAFD_IDX_PGNMSB                     4
#define FAFD_IDX_PGN2ND                     5
#define FAFD_IDX_PGNLSB                     6
#define FAFD_IDX_CHKSUM                     7

#define RXTX_IDX_MSGSTART                   0
#define RXTX_IDX_MSGLENMSB                  1
#define RXTX_IDX_MSGLENLSB                  2
#define RXTX_IDX_MSGID                      3
#define RXTX_IDX_PGNMSB                     4
#define RXTX_IDX_PGN2ND                     5
#define RXTX_IDX_PGNLSB                     6
#define RXTX_IDX_DESTADDR                   7
#define RXTX_IDX_SRCADDR                    8
#define RXTX_IDX_PRIORITY                   9
#define RXTX_IDX_DATASTART                  10

#define RESET_IDX_ULKEY1                    4
#define RESET_IDX_ULKEY2                    5
#define RESET_IDX_ULKEY3                    6

#define SET_IDX_NAME                        4
#define SET_IDX_SA                          12
#define SET_IDX_ADDRRANGE_BOTTOM            13
#define SET_IDX_ADDRRANGE_TOP               14
#define SET_IDX_OPMODE                      15

#define RQ_IDX_REQUESTED                    4

#define RS_IDX_STATUS                       4
#define RS_IDX_SA                           5

/* Command message IDs                                                              */
#define MSG_ID_ACK                          0
#define MSG_ID_FA                           1
#define MSG_ID_FD                           2
#define MSG_ID_TX                           3
#define MSG_ID_RX                           4
#define MSG_ID_RESET                        5
#define MSG_ID_HEART                        6
#define MSG_ID_SETPARAM                     7
#define MSG_ID_RQ                           8
#define MSG_ID_RS                           9
#define MSG_ID_FLASH                        10
#define MSG_ID_SETACK                       11
#define MSG_ID_SETHEART                     12
#define MSG_ID_VERSION                      13
#define MSG_ID_SETPARAM1                    14
#define MSG_ID_SETMSGMODE                   15
#define MSG_ID_TXL                          16

/* RESET unlock key                                                                 */
#define RESET_UNLOCK_KEY1                   0xA5
#define RESET_UNLOCK_KEY2                   0x69
#define RESET_UNLOCK_KEY3                   0x5A

/* Message lengths without overhead (ID + MSGLEN) incl. checksum                    */
#define MSG_LEN_MSB                         0
#define MSG_LEN_ACK                         3
#define MSG_LEN_FA                          5
#define MSG_LEN_FD                          5
#define MSG_LEN_TX                          16
#define MSG_LEN_RX                          16
#define MSG_LEN_RESET                       5
#define MSG_LEN_STATS                       16
#define MSG_LEN_SET                         14
#define MSG_LEN_RQ                          3
#define MSG_LEN_RS                          4
#define MSG_LEN_MM                          3

/* Filters                                                                          */
typedef struct MSGFILTER
{
    long lMsgID;
    bool bMsgActive;
}MsgFilter;

#define MAXFILTER                           100

/* CAN Message Format                                                               */
typedef struct MSG
{
    byte Data[REC_BUFFER_SIZE]; // The maximum J1939 message length 255 x 7 1785
                                // This buffer size provides sufficient space for stuff bytes
    int DataLen;
}Msg;

#endif // CONFIG_H_INCLUDED
