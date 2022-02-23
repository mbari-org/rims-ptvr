import os
import sys
import glob

class FileNameFmt:
    
    def __init__(self, delim='_', ext='.tif'):
        
        # define the required infomation in the file
        # name based on format spec
        self.info_tokens = [
            'deployment', 
            'sys_time',
            'camera',
            'frame_number',
            'roi_number',
            'roi_left',
            'roi_top', 
            'roi_front',
            'roi_width',
            'roi_height',
            'roi_extent',
        ]
        
        # Hold values for tokens here
        self.info_values = {}
        
        # Token delimeter and file extension
        self.delim = delim
        self.ext = ext
        
    def parse_filename(self, filename):
            
        tokens = filename.split('.')[0].split(self.delim)
        
        if len(tokens) != len(self.info_tokens):
            raise ValueError('File name pattern does not match format spec.')
        
        for i, t in enumerate(self.info_tokens):
            self.info_values[t] = str(tokens[i])
    
    def build_filename(self, output_path, delim='_', ext='tif'):
        
        output_name = ''
        
        if len(self.info_values) != len(self.info_tokens):
            raise ValueError('File name info not populated. Populate values before calling this function.')
        
        for t in self.info_values:
            output_name += str(self.info_values[t]) + self.delim
        
        output_name += '.' + self.ext
        
        output_path = os.path.join(output_path, output_name)
        
        return output_path
    
class EyeRISFileNameFmt(FileNameFmt):
    
    def load_from_roi(self, output_path, 
               filename, 
               bb, 
               frame_number,
               roi_number,
               deployment='LRGA2',
               camera='AyeRISCAM00',
               ):
    
        # parse out the roi_info from filename and bounding box
        # Example: 2021-11-11-09-04-06.292372550-000000-
        #dto = datetime.datetime.strptime(filename[0:23] + "UTC",'%Y-%m-%d-%H-%M-%S.%f%Z')
        timestamp = list(filename[0:26])
        timestamp[10] = 'T'
        timestamp = "".join(timestamp).replace('-','') + "Z"
        self.info_values['deployment'] = deployment
        self.info_values['sys_time'] = timestamp
        self.info_values['camera'] = camera
        self.info_values['frame_number'] = str(frame_number)
        self.info_values['roi_number'] = str(roi_number)
        self.info_values['roi_left'] = str(bb[1])
        self.info_values['roi_top'] = str(bb[0])
        self.info_values['roi_front'] = '0'
        self.info_values['roi_width'] = str(bb[3] - bb[1])
        self.info_values['roi_height'] = str(bb[2] - bb[0])
        self.info_values['roi_extent'] = '0'
    
