import os
import unittest
import numpy as np

from amr_kitchen import HeaderData

class TestSliceData(unittest.TestCase):
    pfile2d = "test_assets/example_plt_2d"
    pfile3d = "test_assets/example_plt_3d"

    def test_load2d(self):
        for Lv in [0, 1]:
            hdr = HeaderData(self.pfile2d, limit_level=Lv)
            self.assertIsInstance(hdr, HeaderData)
            self.assertEqual(hdr.ndims, 2)
            self.assertEqual(hdr.limit_level, Lv)

    def test_load3d(self):
        for Lv in [0, 1, 2]:
            hdr = HeaderData(self.pfile3d, limit_level=Lv)
            self.assertIsInstance(hdr, HeaderData)
            self.assertEqual(hdr.ndims, 3)
            self.assertEqual(hdr.limit_level, Lv)

    def test_bybinfile_iterator2d(self):
        hdr = HeaderData(self.pfile2d)
        for lv in range(hdr.limit_level + 1):
            for bfname, offsets, indexes in hdr.bybinfile(lv):
                with open(bfname) as bf:
                    for idx, ofs in zip(indexes, offsets):
                        shape = [idx[1][i] - idx[0][i] + 1 for i in range(hdr.ndims)]
                        shape.append(len(hdr.fields))
                        bf.seek(ofs)
                        arr = np.fromfile(bf, 'float64', np.prod(shape))
                        
    def test_bybinfile_iterator3d(self):
        hdr = HeaderData(self.pfile3d)
        for lv in range(hdr.limit_level + 1):
            for bfname, offsets, indexes in hdr.bybinfile(lv):
                with open(bfname) as bf:
                    for idx, ofs in zip(indexes, offsets):
                        shape = [idx[1][i] - idx[0][i] + 1 for i in range(hdr.ndims)]
                        shape.append(len(hdr.fields))
                        bf.seek(ofs)
                        arr = np.fromfile(bf, 'float64', np.prod(shape))
                    
