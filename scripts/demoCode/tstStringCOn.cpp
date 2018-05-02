#include"iostream"
#include"string.h"

#include <sstream>
std::string Convert (int number){
    std::ostringstream buff;
    buff<<number;
    return buff.str();   
}

int main(){

    int num = 100;
    std::string str;
    str = Convert(num);
    std::cout<<str<< std::endl;
    return 0;
}
