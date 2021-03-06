import os, sys, random, time, filecmp, binascii, binwalk, subprocess

class file_c:
    '''
    Dealing with the file from the filesystem.
    '''
    def __init__(self, filename):
        self.f_fullname = filename                  # blah.jpg
        sz = os.path.getsize(self.f_fullname)       # bytes
        self.f_size = [sz, sz*.001]                 # kilobytes
        f_file = os.path.splitext(self.f_fullname)  # ['blah', 'jpg']
        self.f_name = f_file[0]                     # 'blah'
        self.f_extsn = f_file[-1]                   # 'jpg'
        self.f_types = {}
        self.f_session = str(int(time.time()))      # longass string
        self.pos_bytes = 0 # For get_frags

    def f_frags(self):
        pass
    
    def f_whole(self, hb_type=0):
        '''
        Simply gets whole file into memory at once.
        WARNING: will take lots of memory probably.
        '''
        with open(self.f_fullname, 'rb') as file:
            # Hex wanted
            if hb_type == 0:
                a = binascii.hexlify(file.read())
                return list(a) # Gives int list of hexes [115, 100 ..etc
            # Binary wanted
            elif hb_type == 1:
                a = binascii.hexlify(file.read())
                b = bin(int(a,16))[2:] # Gives giant string
                return [int(n) for n in str(b)]

    def f_folder(self, cleanup=0, shush=True):
        if cleanup==0:
            try:
                os.mkdir(self.f_name)
            except (FileExistsError, OSError) as e:
                if shush:
                    pass
                else:
                    print(f'{e} | {e.args}')
        if cleanup==1:
            try:
                os.rmdir(self.f_name)
                print(f"\n\t[-] Deleted {self.f_name}")
            except (FileExistsError, OSError) as e:
                print(f'{e} | {e.args}')

    def f_type_finder(self, shush=True):
        try:
            for a in binwalk.scan(self.f_fullname, signature=True, quiet=shush, extract=False):
                for b in a.results:
                    self.f_types[f'{b.offset:06x}'] = b.description
        except (FileNotFoundError, binwalk.ModuleException) as e:
            print(f'{e} | {e.args}')

    def f_debug(self):
        """
        Debug options.
        """
        orig_shasum = "".join(subprocess.run(["shasum"], stdout=subprocess.PIPE, text=True, input=f'{self.f_fullname}').stdout[:-2].split())
        print(f'''\n\t[-] TITLE: {self.f_fullname}\tSIZE: {self.f_size[0]} bytes
        \n\t[-] FILE SIGS: {self.f_types}
        \n\t[-] SHASUM: {orig_shasum}\tLEN: {len(orig_shasum)}
        \n\t[-] OS BYTE ORDER: {sys.byteorder}
        ''')

class data_c:
    '''
    Data manipulations shtuff.
    '''
    def __init__(self, data):
        self.d_data = data
        self.d_len = len(data)
    
    def d_shred(self, bitflips=2000, hb_type=0):
        '''
        Take every X amount of bits and flip em'. Will
        cause something to break eventually.
        '''
        # TODO: Maybe make a special terrible no-good hex list?
        for n in range(0, bitflips):
            pin = random.randrange(0, self.d_len)
            # Hex path
            if hb_type == 0:
                # TODO: Shift the hex in whatever direction
                pass
            # Binary path
            elif hb_type == 1:
                # Let the pinpricking begin
                if self.d_data[pin] == 0:
                    self.d_data[pin] = 1
                else:
                    self.d_data[pin] = 0

        return 0
    
    def d_scissor(self):
        '''
        Carefully examining headers, being sure to not mess with things that
        can easily crash the programs involved. Non-chaotic. Intelligent fuzzing.
        - Uses relevant smart methods.
        '''
        # TODO: Stat analysis of file and take those ranges to fuzz
        print("\n\t[*] MUTATED carefully")

    def d_assemble(self, d, hb_type=0):
        '''
        Assembles the data into a writable format.
        hb_type determines if initial data passed in is binary or hexadecimal.
        '''
        # Hex was passed in 
        if hb_type == 0:
            try:
                return binascii.unhexlify(d)
            except binascii.Error as e:
                print(f'Error with assembly: {e}')
        # Binary was passed in
        elif hb_type == 1:
            try:
                return int(d,2).to_bytes(len(d)//8, byteorder='big')
            except (ValueError, TypeError) as e:
                print(f'{e}')
        
        return 0
    
    def d_convert_i2s(self, d_list):
        '''
        Converts a list of ints (1's & 0's) to one string.
        '''
        return "".join([str(t) for t in d_list])
    
    def d_save(self, foldername, filetype='.unknown', session='000', count=0, append=0):
        '''
        Save malformed file to apropos folder.
        '''
        self.newname = f'{session}_{str(count)}{filetype}'
        # For f_whole
        if append == 0:
            with open(os.path.join(foldername, self.newname), 'wb') as f:
                f.write(self.d_data)
        # For f_frags
        elif append == 1:
            # TODO: If getting the file in fragments we go this way
            pass

        return self.newname
    
    def d_delete(self, foldername, filename):
        '''
        Deletes uneeded file.
        '''
        os.remove(f'{foldername}/{filename}')
        return 0