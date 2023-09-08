#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Caesar cypher

bool only_digits(string s);
char rotate(char c, int n);

int main(int argc, string argv[])
{
    //Ensures only one arg
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    //Ensures arg is only digits
    bool isadigit = only_digits(argv[1]);
    if (isadigit == false)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    //Converts the string arg into an int
    int key = atoi(argv[1]);

    //get plaintext from user
    string plaintext = get_string("Plaintext: ");

    //encrypt plaintext
    printf("ciphertext: ");

    int legnth = strlen(plaintext);

    for (int i = 0; i < legnth; i++)
    {
        char letter = plaintext[i];
        char rotated = rotate(letter, key);
        printf("%c", rotated);

    }
    printf("\n");
    return 0;
}

//Returns true if input string only has digits
bool only_digits(string s)
{

    int legnth = strlen(s);

    for (int i = 0; i < legnth; i++)
    {
        char letter = s[i];
        if (isdigit(letter) == false)
        {
            return false;
        }
    }

    return true;
}

char rotate(char c, int n)
{
    if (isalpha(c) == false)
    {
        return c;
    }

    if (isupper(c) == false)
    {
        int lowercase = c - 97;
        int rotated = lowercase + n;
        int wrapped = rotated % 26;
        int rotatedletter = wrapped + 97;

        return rotatedletter;
    }
    else
    {
        int uppercase = c - 65;
        int rotated = uppercase + n;
        int wrapped = rotated % 26;
        int rotatedletter = wrapped + 65;

        return rotatedletter;
    }
}
