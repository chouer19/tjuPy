def checkIfMatch(elem):
    if len(elem) == 5:
        elem = 'aaaaaaaaaaaaaaaaaaaa'
        return True;
    else :
        return False;
 
 
def main():
    
    # List of string 
    listOfStrings = ['Hi' , 'hello', 'at', 'this', 'there', 'from']
    
    # Print the List
    print(listOfStrings)
    
    '''    
        check if element exist in list using 'in'
    '''
    if 'at' in listOfStrings :
        print("Yes, 'at' found in List : " , listOfStrings)
        
    '''    
        check if element NOT exist in list using 'in'
    '''
    if 'time' not in listOfStrings :
        print("Yes, 'time' NOT found in List : " , listOfStrings)    
    
    '''    
        check if element exist in list using count() function
    '''
    if listOfStrings.count('at') > 0 :
        print("Yes, 'at' found in List : " , listOfStrings)
    
    '''    
        check if element exist in list based on custom logic
        Check if any string with length 5 exist in List
    '''
    result = any(len(elem) == 5 for elem in listOfStrings)
    
    if result:
        print("Yes, string element with size 5 found")
    
    '''    
        Check if any string that satisfies the condition in checkIfMatch() function  exist in List
    '''
    result = any(checkIfMatch for elem in listOfStrings)
    
    if result:
        print("Yes, string element with size 5 found")

    print(listOfStrings)
    
        
if __name__ == '__main__':
    main()

