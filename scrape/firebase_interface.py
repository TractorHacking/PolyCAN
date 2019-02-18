from tqdm import tqdm
import sys
import glob

def import_known(path):
    import glob
    for filename in glob.glob(path+'*.md'):
        with open(filename, newline='') as myFile:
            for line in tqdm(myFile):
                if (line[0:7] == "* PGN: "):
                    print("PGN: " + line[7:-1])
                if (line[0:18] == "* Source Address: "):
                    print("PDU Format (PF): " + line[18:-1])
                if (line[0:19] == "* PDU Format (PF): "):
                    print("PDU Format (PF): " + line[19:-1])
                if (line[0:13] == "* Data Page: "):
                    print("Data Page: " + line[13:-1])
                if (line[0:12] == "* Priority: "):
                    print("Priority: " + line[12:-1])
                if (line[0:2] == "| " and line != "| Name | Size | Byte Offset |\n" and line != "| ---- | ---- | ----------- |\n"):
                    tokens = line[2:-3].split(" | ")
                    print(tokens[0])
                    print(tokens[1])
                    print(tokens[2])

        '''
    
            data_length = 



            doc_ref = db.collection(u'known').document(path[:-3]).collection('name')
            db.collection(u'logs').document(path[:-4]).set({u'data_length': length})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['Time'])
                batch.set(line_ref,{ u'pgn': int(line['PGN'], 16),
                                     u'destination': int(line['DA'], 16),
                                     u'source': int(line['SA'], 16),
                                     u'priority': int(line['Priority'], 16),
                                     u'time': float(line['Time']),
                                     u'data': line['Data']
                                     })  
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
        '''
    return    



print("testing\n");
import_known('_idinfo/');

