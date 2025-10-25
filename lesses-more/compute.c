#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <limits.h>

void printInfo(clock_t start, clock_t end, int max){
    double duration = ((double)end-start)/CLOCKS_PER_SEC;
    printf("\nTime taken to execute (seconds): %.3f\n", duration);
    printf("maximum achieved: %d\n", max);
    printf("\n");
}

void printExtremal(int w1, int w2, int w3, int precision, int a, int b, int c, int d, int max){
    printf("(%*d, %*d, %*d, %*d), %*.*f, %*.*f, %*d\n", w1, a, w2, b, w2, c, w2, d, w3, precision, (double)c/b, w3, precision, (double)d/c, w2, max);
}

int f(int a, int b, int c, int d){
    int image = 1;
    while(a != 0 || b != 0 || c != 0 || d != 0){
        image++;
        int tmpA = a;
        a = abs(a-b);
        b = abs(b-c);
        c = abs(c-d);
        d = abs(d-tmpA);
    }
    return image;
}

void brute_search(int n){
    int sums[51];
    for (int i = 0; i < *(&sums+1)-sums; i++){
        sums[i] = INT_MAX;
    }
    
    char domain[51][100];
    for (int i = 0; i < *(&domain+1)-domain; i++){
        strcpy(domain[i], "");
    }
    
    int w1 = 1, w2 = 8, w3 = 5;
    int precision = 3;
    
    clock_t start, end;
    start = clock();
    
    for(int a = 0; a <= n; a++){
        for(int b = 0; b <= n; b++){
            for(int c = 0; c <= n; c++){
                for(int d = 0; d <= n; d++){
                    int image = f(a, b, c, d);
                    int sum = a+b+c+d;
                    if(sum < sums[image]){
                        char buffer[100];
                        sprintf(buffer, "(%*i, %*i, %*i, %*i)", w1, a, w2, b, w2, c, w2, d);
                        strcpy(domain[image], buffer);
                        sums[image] = sum;
                        printExtremal(w1, w2, w3, precision, a, b, c, d, image);
                    }
                }
            }
        }
    }
    
    printf("\n");
    
    for(int i = 1; i < *(&domain+1)-domain; i++){
        if(strcmp(domain[i], "") == 0){
            continue;
        }
        printf("%s %2i\n", domain[i], i);
    }
    
    end = clock();
    printInfo(start, end, -1);
}

void better_search(long n, double low1, double high1, double low2, double high2){
    int a = 0; //assumption after brute force searching 0-999
    long max = 10; //already know that M will be greater than 10 from brute force
    
    int w1 = 1, w2 = 8, w3 = 5;
    int precision = 10;
    
    clock_t start, end;
    start = clock();
    int domain[51][4];
    
    for(int b = 0; b<=n; b++){
        for(int c = round(low1*b); c<=n && c <= round(high1*b); c++){
            for(int d = round(low2*c); d<=n && d <= round(high2*c); d++){
                int image = f(a, b, c, d);
                if (image > max){
                    domain[image][0] = a; domain[image][1] = b; domain[image][2] = c; domain[image][3] = d;
                    max = image;
                    printExtremal(w1, w2, w3, precision, a, b, c, d, max);
                }
            }
        }
    }
    
    end = clock();
    printInfo(start, end, max);
    printf("\nMinimal Input to Achieve Maximum for S = {0 <= a, b, c, d <= %ld}:\n\n%d;%d;%d;%d\n\n", n, domain[max][0], domain[max][1], domain[max][2], domain[max][3]);
}

int main(int argc, char** argv){ 
    better_search(10000000, 2.83928675, 2.83928676, 2.19148787, 2.1914879);
    return 0;
}


/*
 Max values with minimum input up to 999 (true brute force, taking 13 hours---ran over night):
 (a,       b,       c,       d), c/b,               d/c,               f(a, b, c, d)
 (0,       0,       0,       0), nan,               nan,                     1
 (1,       1,       1,       1), 0.000000000000000, 1.000000000000000,       2
 (0,       0,       0,       1), nan,               inf,                     5
 (0,       0,       1,       3), inf,               3.000000000000000,       7
 (0,       1,       2,       4), 2.000000000000000, 2.000000000000000,       8
 (0,       1,       4,       9), 4.000000000000000, 2.250000000000000,       9
 (0,       2,       5,      11), 2.500000000000000, 2.200000000000000,      10
 (0,       2,       6,      13), 3.000000000000000, 2.166666666666667,      11
 (0,       5,      14,      31), 2.800000000000000, 2.214285714285714,      12
 (0,       6,      17,      37), 2.833333333333333, 2.176470588235294,      13
 (0,       7,      20,      44), 2.857142857142857, 2.200000000000000,      14
 (0,      17,      48,     105), 2.823529411764706, 2.187500000000000,      15
 (0,      20,      57,     125), 2.850000000000000, 2.192982456140351,      16
 (0,      24,      68,     149), 2.833333333333333, 2.191176470588236,      17
 (0,      57,     162,     355), 2.842105263157895, 2.191358024691358,      18
 (0,      68,     193,     423), 2.838235294117647, 2.191709844559585,      19
 (0,      81,     230,     504), 2.839506172839506, 2.191304347826087,      20

 
 better_search(10000000, 2.83928675, 2.83928676, 2.19148787, 2.1914879);
 (0,        0,        0,        0),                                    1
 (1,        1,        1,        1),                                    2
 (0,        1,        0,        1),                                    3
 (0,        0,        1,        1),                                    4
 (0,        0,        0,        1),                                    5
 (0,        1,        2,        3),                                    6
 (0,        0,        1,        3),                                    7
 (0,        1,        2,        4),                                    8
 (0,        1,        4,        9),                                    9
 (0,        2,        5,       11),                                   10
 (0,        2,        6,       13), 3.0000000000, 2.1666666667,       11
 (0,        5,       14,       31), 2.8000000000, 2.2142857143,       12
 (0,        6,       17,       37), 2.8333333333, 2.1764705882,       13
 (0,        7,       20,       44), 2.8571428571, 2.2000000000,       14
 (0,       17,       48,      105), 2.8235294118, 2.1875000000,       15
 (0,       20,       57,      125), 2.8500000000, 2.1929824561,       16
 (0,       24,       68,      149), 2.8333333333, 2.1911764706,       17
 (0,       57,      162,      355), 2.8421052632, 2.1913580247,       18
 (0,       68,      193,      423), 2.8382352941, 2.1917098446,       19
 (0,       81,      230,      504), 2.8395061728, 2.1913043478,       20
 (0,      193,      548,     1201), 2.8393782383, 2.1916058394,       21
 (0,      230,      653,     1431), 2.8391304348, 2.1914241960,       22
 (0,      274,      778,     1705), 2.8394160584, 2.1915167095,       23
 (0,      653,     1854,     4063), 2.8392036753, 2.1914778857,       24
 (0,      778,     2209,     4841), 2.8393316195, 2.1914893617,       25
 (0,      927,     2632,     5768), 2.8392664509, 2.1914893617,       26
 (0,     2209,     6272,    13745), 2.8392937981, 2.1914859694,       27
 (0,     2632,     7473,    16377), 2.8392857143, 2.1914893617,       28
 (0,     3136,     8904,    19513), 2.8392857143, 2.1914869721,       29
 (0,     7473,    21218,    46499), 2.8392881038, 2.1914883589,       30
 (0,     8904,    25281,    55403), 2.8392857143, 2.1914876785,       31
 (0,    10609,    30122,    66012), 2.8392873975, 2.1914879490,       32
 (0,    25281,    71780,   157305), 2.8392864206, 2.1914878796,       33
 (0,    30122,    85525,   187427), 2.8392868999, 2.1914878690,       34
 (0,    35890,   101902,   223317), 2.8392867094, 2.1914879001,       35
 (0,    85525,   242830,   532159), 2.8392867583, 2.1914878722,       36
 (0,   101902,   289329,   634061), 2.8392867657, 2.1914878909,       37
 (0,   121415,   344732,   755476), 2.8392867438, 2.1914878804,       38
 (0,   289329,   821488,  1800281), 2.8392867635, 2.1914878854,       39
 (0,   344732,   978793,  2145013), 2.8392867503, 2.1914878835,       40
 (0,   410744,  1166220,  2555757), 2.8392867577, 2.1914878839,       41
 (0,   978793,  2779074,  6090307), 2.8392867542, 2.1914878841,       42
 (0,  1166220,  3311233,  7256527), 2.8392867555, 2.1914878838,       43
 (0,  1389537,  3945294,  8646064), 2.8392867552, 2.1914878840,       44

 Time taken to execute (seconds): 0.629
 maximum achieved: 44
 total iterations: 1731232

 Minimal Input to Achieve Maximum for S = {0 <= a, b, c, d <= 10000000}:

 0;1389537;3945294;8646064
 
 */
