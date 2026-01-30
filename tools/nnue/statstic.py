import os
import json

def get_filepaths(directory,extension="txt"):
    filepaths = []
    for root,dirs,files in os.walk(directory):
        for _file in files:
            if _file.endswith(extension):
                filepaths.append(os.path.join(root,_file))
    print("size of filepaths = ",len(filepaths))
    return filepaths

if __name__ == "__main__":
    filepaths = get_filepaths(directory=r"data",extension="json")
    cnt = 0
    for file_idx,filepath in enumerate(filepaths):
        json_data = json.load(open(filepath,"r",encoding="utf-8"))
        for base_status in json_data:
            cnt += len(base_status['data'][0]['data'])
        print(file_idx + 1,len(filepaths))
        print(cnt,cnt * len(filepaths) // (file_idx + 1))