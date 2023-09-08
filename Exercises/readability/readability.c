#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

int count_letters(string text);
int count_words(string text);
int count_sentances(string text);

int main(void)
{

    //get text from the user
    string words = get_string("Text: ");
    int count = count_letters(words);
    int wordcount = count_words(words);
    int sentcount = count_sentances(words);

    float L = ((float)count / (float)wordcount) * 100;

    float S = ((float)sentcount / (float)wordcount) * 100;

    int index = round(0.0588 * L - 0.296 * S - 15.8);

    if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (index < 16)
    {
        printf("Grade %d\n", index);
    }
    else
    {
        printf("Grade 16+\n");
    }

}

//count letters
int count_letters(string text)
{

    int counter = 0;

    int legnth = strlen(text);

    for (int i = 0; i < legnth; i++)
    {
        char letter = text[i];
        if (isalpha(letter))
        {
            counter++;
        }
    }

    return counter;
}

//count words
int count_words(string text)
{
    // if white space increase words by one if not do not increase word count
    int counter = 1;

    int legnth = strlen(text);

    for (int i = 0; i < legnth; i++)
    {
        char hwords = text[i];
        if (isspace(hwords))
        {
            counter++;
        }
    }

    return counter;

}

//counts sentances
int count_sentances(string text)
{
    int counter = 0;

    int legnth = strlen(text);

    for (int i = 0; i < legnth; i++)
    {
        char letter = text[i];
        if (letter == '!' || letter == '.' || letter == '?')
        {
            counter++;
        }
    }

    return counter;

}