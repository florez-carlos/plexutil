from html import escape
import urllib.parse
import typing

class  QueryBuilder():

    def __init__(self,path: str = "", **kwargs):
        self.path = path
        self.query_parameters = kwargs


    def build(self) -> str:

        result = self.path

        if self.query_parameters:
            result += "?"

        result += self.__walk__(self.query_parameters)


        #Remove the last &
        if self.query_parameters:
            result = result[:-1]

        return result 
    
    def __walk__(self, path: typing.Dict[str,str] | typing.Dict[str,bool] | typing.Dict[str,int] = {},nested_parent_name: str = "") -> str:

        result = ""


        for k,v in path.items():

            if k == "the_type":
                k = "type"

            if isinstance(v,bool):

                if v:
                    v = "1"
                else:
                    v = "0"
                    
            if isinstance(v,int):

                v = str(v)

            if isinstance(v,dict):

                result += self.__walk__(v,k)
                continue

            v = urllib.parse.quote(v)

            if nested_parent_name:
                bracket_open = urllib.parse.quote("[")
                bracket_close = urllib.parse.quote("]")
                result +=  nested_parent_name + bracket_open + k + bracket_close +"="+v+"&"
                continue

            result +=  k+"="+v+"&"
            
        return result








