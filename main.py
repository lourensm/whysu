import sys

mylist = [
            [0,0,0,0,0,6,0,0,0],
            [7,8,0,0,4,0,0,0,0],
            [0,0,1,0,3,5,0,0,0],
    [0,5,0,2,0,0,0,0,0],
    [2,0,0,0,8,0,0,1,0],
    [0,0,0,1,0,0,0,0,3],
    [0,6,2,0,0,8,0,0,0],
    [0,7,8,5,0,0,0,4,0],
    [0,0,0,0,0,0,0,0,0]
         ]

"""attempt at deep copy of mylist
sudoarray = [[]]*9
for col in range(0,9):
    row = mylist[col]
    row = row[:]
    print col
    sudoarray[col] = row
"""
from copy import deepcopy
sudoarray = deepcopy(mylist)


"""
Program solves at least one sudoku puzzle.
Sudoku variant with additional constraints of 4  3x3 squares.

Inspired by recent publicity on Singapore Prime Minister Lee Hsien Loong.

Additionally I followed the same procedure I use when solving it on paper.
I wondered what rules are sufficient to solve a sudoku.

The algorithm is simple:
for each column 
   each entry within the column
        check within the 3*9 values whether value can be filled in 
           due to:
               other column in 3*9 not available, or containing value already
               and of the triple in this other column there is only one position where
               value can be placed.
for each set of 9 cells with unique value constraint, check if single value is missing/

This is a bit suspect as I sometimes seemed to need filling in missing values by constraining to
subsets of values in subsets of cells.

Horrible performance:
No structure maintained of todo list.
No structure maintained per 9 cell unique entry.

advanced solution would be to have set value update to check later aspects.

Action:
    If I find a sudoku that seems not to be solvable this way, check again.
"""









def sudo(col, row, rot):
    "access to sudo array"
    if rot:
        return sudoarray[row][col]
    return sudoarray[col][row]


def set_sudo(col, row, rot, val):
    "set sudo array value"
    if rot:
        sudoarray[row][col] = val
    else:
        sudoarray[col][row] = val

def entryin(rowcol):
    """topleft index of gray area we are part of"""
    if rowcol < 1:
        return 0
    elif rowcol < 4:
        return 1
    elif rowcol < 5:
        return 0
    elif rowcol < 8:
        return 5
    else:
        return 0

def nextentrysametriple(rowcol):
    return 3*(rowcol//3) + (rowcol%3 + 1)%3

def preventrysametriple(rowcol):
    return 3*(rowcol//3) + (rowcol%3 + 2)%3

class otherentrysametriple:
    def __init__(self, rowcol):
        assert(0 <= rowcol and rowcol < 9)
        self.i = 0
        self.rowcol = rowcol
        self.done = 0

    def __iter__(self):
        return self

    def next(self):
        if self.done < 2:
            r = self.i
            self.i += 1
            self.done += 1
            self.rowcol = nextentrysametriple(self.rowcol)
            return self.rowcol
        else:
            raise StopIteration()

def nexttriple(triple):
    return 3*((triple//3 + 1)%3)

def prevtriple(triple):
    return 3*((triple//3 + 2)%3)

class othertriples:
    def __init__(self, triple):
        assert(triple%3 == 0)
        self.triple = triple
        self.done = 0

    def __iter__(self):
        return self

    def next(self):
        if self.done < 2:
            self.triple = nexttriple(self.triple)
            self.done += 1
            return self.triple
        else:
            raise StopIteration()


class othercolsrowtriples:
    def __init__(self, col, rowtriple):
        assert(rowtriple % 3 == 0)
        self.done = 0
        self.col = col
        self.rowtriple = rowtriple

    def __iter__(self):
        return self

    def next(self):
        if self.done == 0:
            self.done += 1
            return ((nextentrysametriple(self.col), nexttriple(self.rowtriple)),
                    (preventrysametriple(self.col), prevtriple(self.rowtriple)))
        elif self.done == 1:
            self.done+=1
            return ((nextentrysametriple(self.col), prevtriple(self.rowtriple)),
                    (preventrysametriple(self.col), nexttriple(self.rowtriple)))
        else:
          raise StopIteration()

def lastentryintriple(rowcol1, rowcol2):
    assert(rowcol1//3 == rowcol2//3)
    res = rowcol1//3 + 3 - rowcol1%3 - rowcol2%3
    assert(res//3 == rowcol1//3)
    assert(res != rowcol1 and res != rowcol2)
    return res

    
def lasttriple(triple1, triple2):
    assert(triple1%3 == 0)
    assert(triple2%3 == 0)
    assert(triple1 != triple2)
    return (3 - triple1//3 - triple2//3)*3 

def valoccursinrow(val, col, startrow, rot):
    """return 1 if val occurs in col, startrow triple"""
    for row4 in range(startrow,startrow+3):
        if sudo(col,row4, rot) == val:
            return 1
    return 0

def testrowval(val, col, row, rot):
    """characterize col, row wrt val and whole row presence
    has val 0, can be available for val 1, is unavailable for val 2"""
    valo = sudo(col,row,rot)
    if valo == val:
        return 0
    if valo != 0:
        return 2
    
    #check for perpendicular occurrence of val
    foundp = 0
    #check for occ val in whole row4
    for coln in range(0,9):
        #should check only other 3s
        if sudo(coln,row,rot) == val:
            return 2
        colin = entryin(col)
        #check occurrence in gray area
        #first brute force, later limit not self 3
        #is costly so probably wait for >= 2 empty?
        rowin = entryin(row)
        if colin != 0 and rowin != 0:
            for colg in range(colin, colin+3):
                for rowg in range(rowin,rowin+3):
                    if sudo(colg,rowg, rot) == val:
                            return 2
    return 1


def colrowtriplenotval(val, col,startrow,rot):
    """check this column, the triple starting at startrow, exit 1 if triple cannot hold val. 
val should not occur in row (should be part of separate test as this test is more expensive.
"""
    assert(not valoccursinrow(val, col, startrow, rot))
    assert(startrow%3 == 0)
    for row in range(startrow, startrow+3):
        res = testrowval(val, col, row, rot)
        if res == 0:
            print("ERROR", col, row, val, rot)
            raise RuntimeError("wrong call colrowtriplenotval")
            sys.exit(1)
        elif res == 1:
            return 0
    return 1
        
def print_set(col, row, rot, val):
    if rot:
        print("FILLED in",row, col,"value",val)
    else:
        print("FILLED in",col, row,"value",val)


def checkvalcolrowtriple(val, col2, row3, rot):
    """knowing val should be in col2, triple(row3), fill in val"""
    #is val already in col2,triple row3?"""
    assert(row3%3 == 0)
    assert(not valoccursinrow(val, col2, row3, rot))
    #detect which 3 elements
    cand = -1
    candidates = 0
    for row4 in range(row3, row3+3):
        #check filled by some means
        res = testrowval(val, col2, row4, rot)
        if res == 1:
            cand = row4
            candidates += 1
            if candidates > 1:
                return 0
        elif res == 0:
            #already dealt with....
            print "Should have been checked"
            sys.exit(1)
            return 0
    if candidates == 1:
        set_sudo(col2,cand,rot, val)
        print_set(col2, cand, rot, val)
        return 1
    else:
        #candidates == 0: val should be in triple!
        print("Unexpected result", val, col2, row3, rot, candidates)
        sys.exit(12)

def checkmissingrow(col, rot):
    # we need the values present, we need the coordinates missing values
    # we need the values missing
    missingvals = [1]*10
    missing = 9
    emptycells = []
    lowestvalmissing = 0
    for row in range(0,9):
        val = sudo(col, row, rot)
        if val != 0:
            missingvals[val] = 0
            missing -= 1
        else:
            emptycells.append((col, row, rot))
    return handlemissing(missing, missingvals, emptycells)

def checkmissing33(col0, row0):
    missingvals = [1]*10

    missing = 9
    emptycells = []
    lowestvalmissing = 0
    rot = 0
    for col in range(col0, col0+3):
        for row in range(row0, row0+3):
            val = sudo(col, row, rot)
            if val != 0:
                missingvals[val] = 0
                missing -= 1
            else:
                emptycells.append((col, row, rot))
    return handlemissing(missing, missingvals, emptycells)
    
def handlemissing(missing, missingvals, emptycells):    
    if missing == 0:
        return 0
    if missing == 1:
        missingval = 0
        for val in range(1,10):
            if missingvals[val] == 1:
                missingval = val
                break
        assert(missingval != 0)
        assert(len(emptycells)==1)
        (col, row, rot) = emptycells[0]
        set_sudo(col,row,rot, missingval)
        print_set(col, row, rot, missingval)
        return 1
    else:
        # later try more advanced stuff
        return 0
    
def missingvalues():
    """for each 9-tuple, check necessary value.
first only single missing value, later pairs, later still, sets of values"""
    changed = 0
    for rot in [0,1]:
        for col in range(0,9):
            changed += checkmissingrow(col, rot)
    for tstart in [(1,1), (1,5), (5,1),(5,5)]:
        (col, row) = tstart
        changed += checkmissing33(col, row)

    for col in [0,3,6]:
        for row in [0, 3, 6]:
            changed += checkmissing33(col, row)
    return changed

def handletwonines(rot):
    changed = 0
    for col in range(0,9):
        for row in range(0,9):
            val = sudo(col, row, rot)
            rowtriple = row - row%3
            odone = 0
            if val != 0:
                #                for ((col1, rowstart1),(col2, rowstart2))
                for a in othercolsrowtriples(col,rowtriple):
                    ((col1, rowstart1), (col2,rowstart2)) = a
                    """ hasval, hasval
                        hasval ->  checkvalfound
                        checkvalfound <- hasval
                        cannot have val -> othersituation
"""
                    if valoccursinrow(val, col1, rowstart1, rot):
                        odone = 1
                        if not valoccursinrow(val, col2, rowstart2, rot):
                            if checkvalcolrowtriple(val, col2, rowstart2,rot):
                                changed += 1
                    elif valoccursinrow(val, col2, rowstart2, rot):
                        odone = 1
                        if checkvalcolrowtriple(val, col1, rowstart1, rot):
                            changed += 1
                    elif (colrowtriplenotval(val, col1, rowstart1, rot) or \
                        colrowtriplenotval(val, col2, rowstart2, rot)):
                        odone1 = 1
                        #check two other colrows
                        #col1, rowstart2, col2, rowstart1
                        if not valoccursinrow(val, col1, rowstart2, rot):
                            if checkvalcolrowtriple(val, col1, rowstart2, rot):
                                changed += 1
                        if not valoccursinrow(val, col2, rowstart1, rot):
                            if checkvalcolrowtriple(val, col2, rowstart1, rot):
                                changed += 1
                    if odone:
                        break
    return changed
                    

#DEBUG: next vertical 2,2 FILLED

while 1:
    changed = 0
    print "NORMAL"
    changed += handletwonines(0)
    print "ROT"
    changed += handletwonines(1)
    print "MISSING"
    changed += missingvalues()
    print("END changed", changed)
    if changed == 0:
        break

print "original:",mylist

print "solved:", sudoarray

rot = 0
for col in range(0,9):
    for row in range(0,9):
        if sudo(col, row, rot) == 0:
            print("col:",col, "row:", row)
            raise RuntimeError("Result incomplete:apparently need more checks")
print "Sudoku solved"






                            
                                
                            
        

    
