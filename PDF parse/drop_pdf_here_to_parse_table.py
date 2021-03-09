import tabula
import traceback
import sys
for filename in sys.argv[1:]: 
    print(filename)
    print(filename[:-4]+".csv")
    try:
        tabula.convert_into(filename, filename[:-4]+".csv", output_format="csv", pages='all', stream=True, guess=True, lattice=True)
    except Exception as e:
        traceback.print_exc()
input("Press ANY key...")