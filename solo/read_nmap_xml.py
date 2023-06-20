from typing import Any
from bs4 import BeautifulSoup
 
class c_nmap_read:
    def f_read_nmap(file: str):
        with open(file, 'r') as f:
            data = f.read()
        
        Bs_data = BeautifulSoup(data, "xml")
        
        # Finding all instances of tag
        # `unique`
        b_unique = Bs_data.find_all('port')
        
        x = Bs_data.findChildren('port')
        for i in x:
            if(str(i).find("open")):
                Tstr = str(i).split(" ")
                for val in Tstr:
                    print(f"{val}")


        # Using find() to extract attributes
        # of the first instance of the tag
        """         b_name = Bs_data.find('port', recursive='true')
        
        for x in b_name:
            print(f'name:{b_name.get("portid")}')
            if(b_name!= None):
                # Extracting the data stored in a
                # specific attribute of the
                # `child` tag
                value = b_name.get("port")
                
                print(value) """
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.f_read_nmap(self, *args, **kwds)

c_nmap_read.f_read_nmap("/home/muser/localhost.xml")