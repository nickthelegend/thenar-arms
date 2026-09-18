"""Slice the encoder leader; publish geometry only until layer review."""
import slice_follower_r3 as slicer
from build_encoder_leader import DEST

if __name__=='__main__':
    slicer.DEST=DEST
    slicer.main()
