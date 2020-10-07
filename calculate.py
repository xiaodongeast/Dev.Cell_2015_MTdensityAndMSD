"""
|-------------------------------------------------------|
|       This is for calculation of MT space.            |
|The input data should be from Image J macro Drawline2  |
|required package : pandas, numpy, scipy, sys, os       |
|usage: in the shell, type the following line:          |
|******************                                     |
|Python calculate.py filename correctX corrctionY       |
|******************                                     |
|contact  Xiaodong if you still have problem            |
---------------------------------------------------------
"""


import pandas as pd
import numpy as np
from scipy.spatial import distance
import sys,os


class LengthNotMatchError(Exception):
    """
    Exception for 0 255 not matching
    """
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        if self.start > self.stop:
            msg = '---Error!!!! you have more start point(255)'
        elif self.start < self.stop:
            msg = '---Error!!!! you have more stop point(0)'
        super().__init__(msg)


class Spacer:
    """
    The class to calculate MT density.
    user can only two methods:

    read_txt() to read the input txt file.
    run() to compute the result and save the result to the same folder as the input txt file
    __str__ is overwrite to show the input file content as a dictionary.

    The format: input file needs to be generated from the image J macro without change

    """

    def __init__(self):
        self.line_dict ={}

    def read_txt(self,file_path):
        df = pd.read_csv(file_path, delimiter=r'\s+', header = None, index_col = False)
        df.columns =['line_no','x_pos', 'y_pos','intensity']
        return df

    def _split_line(self, df):
        """

        :param data frame after read the txt from image j
        :return: a dictionary

        """

        try:
            line_nums = df.line_no.max()
            for i in range(line_nums+1):
                self.line_dict[i] = df[df.line_no == i]
                # print('this is no line', self.line_dict[i])
        except AttributeError as error:
            print('---Error!!!!')
            print('your data frame nameing problem duble check')
            print(error)

    def _validate_line(self, xcol =1, ycol=2,correct_x=1024, correct_y =1024):
        """
        the rule for checking:
        every line need to start with 255(backgroud), end with 255(background)
        position need to ne within the boundary
        :return:  True means c2rrect, False means user need to check

        """
        is_validate = True
        for lineNo in self.line_dict:
            line = self.line_dict[lineNo]
            idx_pos = (line.iloc[:, xcol] * line.iloc[:, ycol]) < 0
            idx_pos_x = line.iloc[:, xcol] >= correct_x
            idx_pos_y = line.iloc[:, ycol] >= correct_y
            if sum(idx_pos) > 0:
                print('--warning!!!', lineNo, 'starting out of boundary, cut the negaive value')
            if sum(idx_pos_x) >0 :
                print('correct x out of boundary')
            if sum(idx_pos_y) > 0:
                print('correct y out of boundary')
            idx_correct = (~idx_pos) & (~idx_pos_x) & (~idx_pos_y)

            # update the dictionary
            self.line_dict[lineNo] = line[idx_correct]

            try:
                line = self.line_dict[lineNo].intensity.values
                print('-----',lineNo)
                print(line)
            except AttributeError as error:
                print('---Error!!!!your data frame nameing problem for intensity duble check')

            if not (line[0] == 255 and line[-1] == 255):
                print(''' your line need to start from background(0,0)
                Your No.{} line is wrong
                the starting value is:{}
                the stopping value is :{} '''.format(lineNo, line[0], line[-1]))
                is_validate = False
        return is_validate

    def _dis_cal(self,start,stop,index = 0):
        """
        :param start: a numpy 2D array of the starting x and y
        :param stop:  a numpy 2D array of stopping and y
        :return: distance with the index column by default is zero
        """

        dis_mat = distance.cdist(start,stop, 'euclidean')
        result = np.diag(dis_mat)
        idx_col = np.ones(result.size) * index

        #print('----',index, start, stop)
        return np.reshape(np.column_stack((idx_col,result)),(-1,2))

    def _dis_lines(self, intensity_col =3,  xcol =1, delta =2):
        """
        calcaulate distance for all the lines
        private do not use
        :return:
        """
        mask = self._mask()
        start_intensity = 255
        stop_intensity =0 # this include the boundary and the space
        result_array = np.array([], dtype=np.int64).reshape(0,2)


        for lineNo in mask:
            line= mask[lineNo]
            start = line[line.iloc[:,intensity_col] == start_intensity ]
            stop = line[line.iloc[:,intensity_col] == stop_intensity ]

            #print( '---',lineNo,'--- \n',line, stop, start,len(start), len(start))
            if len(stop) != len(start):
                raise LengthNotMatchError(len(start), len(stop))
            result = self._dis_cal(start.iloc[:,xcol:xcol+2].values, stop.iloc[:,xcol:xcol+2].values, lineNo)
            result_array = np.vstack((result_array, result))
        result_df =pd.DataFrame({'lineNo': result_array[:,0], 'space': result_array[:,1]})

        return result_df

    def _mask(self,intensity_col = 3):
        """
        this function takes the difference with the steping size of 1 to find the boundary.
        :param intensity_col by default pixel intensity is at the 3rd column
        :return:
        """
         # intensity need to be the 3rd
        cut_off = 0
        mask ={}
        for lineNo in self.line_dict:

            line = self.line_dict[lineNo]
            # diff, each one is the minus the previous, so 255 is starting, -255 is ending
            # remove out of boundary

            line_diff = line.diff()
            idx = line_diff.iloc[:,intensity_col] != cut_off

            # take the none zero as the useful info, remove the first two and last
            selected = line[idx].copy()
            selected = selected.iloc[2:-1,:]
            mask[lineNo] = selected

        return mask

    def run(self, save_path, file_path, correct_x = 165, correct_y = 164):
        """
        This is for the user, to use. just put everything together
        :param file_path:
        :param correct_x:
        :param correct_y:
        :return:
        """

        pd.set_option('display.max_rows', None)
        df = self.read_txt(file_path)
        self._split_line(df)
        is_valid = self._validate_line(correct_x= correct_x, correct_y =correct_y)

        if not is_valid:
            print('data set not valid')
            return

        result = self._dis_lines()
        result.to_csv(save_path, index = False)
        return result

    def __str__(self):

        return "the line scans: {}".format(self.line_dict)


if __name__ =='__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print(__doc__)

    try:
        file_path =  sys.argv[1]

        file_name = os.path.split(file_path)[1]
        file_name = file_name.split('.')[0]
        save_name = 'result_' + file_name + '.csv'
        save_path = os.path.join(os.path.split(file_path)[0], save_name)

        correct_x = int(sys.argv[2])
        correct_y = int(sys.argv[3])
        print('your input',file_path, correct_x, correct_y, save_path)
        solver = Spacer()

        solver.run(save_path, file_path, correct_x, correct_y)

    except IndexError as e:
        print('Error!',e)
        print(__doc__)


