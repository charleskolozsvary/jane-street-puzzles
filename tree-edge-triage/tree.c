#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/*
 * From: http://robotics.stanford.edu/users/sahami/cs121/code/random.c
 * Function: InitRandom
 * --------------------
 * This function seeds the random number generator
 * with the current time.  It should be called once
 * (and only once) prior to calling any other random
 * number function.
 */

void initRandom(void)
{
  srand((int) time(NULL));
}
/*
 * Function: RandomReal
 * --------------------
 * This function returns a random real number between
 * low and high, inclusive.
 */
double randomReal(double low, double high)
{
  double d;
  d = (double) rand() / ((double) RAND_MAX + 1);
  return (low + d * (high - low));
}

struct linkedList{
    long idx;
    struct linkedList * next;
};

struct linkedList * makeLL(long rootVal){
    struct linkedList * ll = (struct linkedList *)calloc(sizeof(struct linkedList), 1);
    return ll;
}
void insertLL(long val, struct linkedList * ll){
    struct linkedList * after = ll->next;
    ll->next = (struct linkedList *)calloc(sizeof(struct linkedList), 1);
    ll->next->idx = val;
    (*(*ll).next).next = after;
}

int lengthOfLL(struct linkedList * head){
    int count = 0;
    while (head != NULL) {
        count++;
        head = head->next;
    }
    return count-1;
}

void printLL(struct linkedList *ll){
    printf("LinkedList contents:\n");
    while (ll != NULL) {
        printf("%li\n", ll->idx);
        ll = ll->next;
    }
    printf("%p\n", ll);
}
struct linkedList * reverseLL(struct linkedList * curr){
    struct linkedList * prev = NULL;
    struct linkedList * after;
    while (curr != NULL) {
        after = curr->next;
        curr->next = prev;
        prev = curr;
        curr = after;
    }
    return prev;
}

void removeLL(struct linkedList * delete, struct linkedList * prev){
    struct linkedList * after = delete->next;
    free(delete);
    if (prev != NULL)
        prev->next = after;
}

short inLL(long val, struct linkedList * curr){
    while(curr != NULL){
        if (curr->idx == val)
            return 1;
        curr = curr->next;
    }
    return 0;
}

struct node{
    short val;
    struct node * left;
    struct node * right;
};

int geti(int num){
    int idx = 0;
    while (num > 0){
        num >>= 1;
        idx++;
    }
    return idx-1;
}

void nSpaces(long n){
    for (long i = 0; i < n; i++){
        printf(" ");
    }
}

/*
 wll is a linked list of the indices of the nodes that are part of the 'winning cascade'.
 */
void extendLines(long numOfSplits, long width, long height, long startRowIdx, int spacer, struct linkedList * wll){
    long innerWidth = 1;
    for (long i = 0; i < height-1; i++){
        nSpaces(2);
        for (long j = 0; j < numOfSplits; j++){
            nSpaces(width-1);
            inLL(startRowIdx + j*2, wll) ? printf("/") : printf(" ");
            nSpaces(innerWidth);
            inLL(startRowIdx + j*2 + 1, wll) ? printf("\\") : printf(" ");
            nSpaces(width-1);
            nSpaces(spacer);
        }
        printf("\n");
        width--;
        innerWidth += 2;
    }
}

void printNodes(long numNodes, long width, struct node * nodePres, int level, int spacer){
    printf("%i ", level+1);
    for (long i = 0; i < numNodes; i++){
        nSpaces(width);
        nodePres[i].val ? printf("A") : printf("B");
        nSpaces(width);
        nSpaces(spacer);
    }
    printf("\n");
}

void printBTree(int depth, struct node * treeArr, struct linkedList * wll, int doShort){
    int spacer = 3;
    long height = pow(2, depth); //total # of "\n" divided by 2
    long width = pow(2, depth);
    for (int i = 0; i < depth; i++){
        long startRowIdx = (long)pow(2, i+1)-1;
        if (!doShort)
            extendLines((long)pow(2, i), (long)pow(2, depth+1-i)-2, height, startRowIdx, spacer, wll);
        printNodes((long)pow(2, i+1), width-2, &treeArr[startRowIdx], i, spacer);
        width /= 2; height /= 2;
    }
}

void recMakeTree(double, long, long, struct node *, int);

short canWin(struct node *, int);
short winRec(int, long, struct node *, int);
short ** generateEnc(long);
struct node * makeFixedTree(int, short *);

void printShort(short * toPrint, long len){
    for (long i = len-1; i >= 0; i--){
        printf("%u", toPrint[i]);
    }
    printf("\n");
}

long scoreShort(short * enc, long len){
    long score = 0;
    for (long i = 0; i < len; i++){
        score += enc[i];
    }
    return score;
}

/*
 Give the number of winning trees out of the total
 2^(2^(depth+1)-2) possible labeled game trees for finite depth 'depth'
 */
long bruteForceWinningOrientations(int depth){
    double win = 0, lose = 0;
    long winCount = 0;
    long numEdges = pow(2, depth+1)-2;
    short ** encodings = generateEnc(numEdges);
    for (long i = 0; i < pow(2, numEdges); i++){
        struct node * tree = makeFixedTree(depth, encodings[i]);
        long numAs = scoreShort(encodings[i], numEdges);
        if (canWin(tree, depth)){
            winCount++;
        }
    }
    printf("winning/total:%li/%ld\npercentage:\n%3.6f\n", winCount, (long)pow(2, numEdges), (double)winCount/pow(2, numEdges));
    return winCount;
}

/*
 For all 2^numEdges possible game trees, create an array of shorts that
 encode which edges are A and which are B.
 We let each number in [0, 2^numEdges] correspond to such an encoding
 */
short ** generateEnc(long numEdges){
    long totNum = pow(2, numEdges);
    short ** encodings = (short **)calloc(sizeof(short *), totNum);
    for (long i = 0; i < totNum; i++){
        long encnum = i;
        short * encoding = (short *)calloc(sizeof(short), numEdges);
        for (int j = 0; j < numEdges; j++){
            short rightmost = ((encnum >> 1) << 1) ^ encnum;
            encoding[j] = rightmost;
            encnum >>= 1;
        }
        encodings[i] = encoding;
    }
    return encodings;
}

struct node * makeFixedTree(int depth, short * encoding){
    // not pow(2, depth+1)-2 since we include the very first
    // node even though the game doesn't care about it  
    long numEdges = pow(2, depth+1)-1; 
    struct node * rootaddr = (struct node*)calloc(sizeof(struct node), numEdges);
    rootaddr[0] = (struct node){1, NULL, NULL};
    for (int i = 0; i < numEdges-1; i++){
        rootaddr[i+1] = (struct node){encoding[i], NULL, NULL};
    }
    return rootaddr;
}

/*
 For a given depth create a tree and label each edge independently either A or B
 with probability p or 1-p respectively.
*/
struct node * makeTree(double p, int depth){
    struct node * rootaddr = (struct node *)calloc(sizeof(struct node), pow(2, depth+1)-1);
    rootaddr[0] = (struct node){1, NULL, NULL};
    recMakeTree(p, 1, 0, rootaddr, depth);
    recMakeTree(p, 1, 1, rootaddr, depth);
    return rootaddr;
}


void recMakeTree(double p, long i, long j, struct node * rootAddr, int depth){
    long idx = pow(2, i) + j - 1;
    if (i == depth){
        rootAddr[idx].val = randomReal(0, 1) <= p;
        return;
    }
    if (i > depth){
        return;
    }
    if (randomReal(0, 1) <= p){ //can go down on Aaron's turn
        (rootAddr+idx)->val = 1;
        long leftIdx = (long) pow(2, i+1) + 2*j - 1, rightIdx = leftIdx + 1;
        (rootAddr+idx)->left  = rootAddr+leftIdx;
        (rootAddr+idx)->right = rootAddr+rightIdx;
        (rootAddr+leftIdx)->val = randomReal(0, 1) <= p;
        (rootAddr+rightIdx)->val = randomReal(0, 1) <= p;
        if (rootAddr[leftIdx].val && rootAddr[rightIdx].val){ //can proceed past Beren's turn
            recMakeTree(p, i+2, 2*2*j + 0, rootAddr, depth); //the first of Aaron's possible paths down
            recMakeTree(p, i+2, 2*2*j + 1, rootAddr, depth); //the second of Aaron's possible paths down
            recMakeTree(p, i+2, 2*2*j + 2, rootAddr, depth); //& c.
            recMakeTree(p, i+2, 2*2*j + 3, rootAddr, depth);
        }
//        else{
//            rootAddr[leftIdx].val = rootAddr[leftIdx].val ? 1 : 0;
//            rootAddr[rightIdx].val = rootAddr[rightIdx].val ? 1 : 0;
//        }
    }
}

short cascadeRec(int, long, struct node *, struct linkedList *, int);

/*
 Figure out whether Aaron wins for a given tree.
 Return the pointer to a linked list that includes the winning edges
 (or rather, the indices of said edges) if Aaron can win.
 */
struct linkedList * winningCascade(struct node * tree, int depth){
    struct linkedList * winningIndices = makeLL(0);
    short res = cascadeRec(0, 0, tree, winningIndices, depth);
    if (res){
        struct linkedList * newHead = winningIndices->next;
        removeLL(winningIndices, NULL);
        return newHead;
    }
    else
        return NULL;
}

short searchAndRemove(long val, struct linkedList * wll){
    struct linkedList * prev = NULL;
    while (wll != NULL){
        if (wll->idx == val){
            removeLL(wll, prev);
            return 1;
        }
        prev = wll;
        wll = wll->next;
    }
    return 0;
}

void removeRec(int, long, struct linkedList *, int);

void removeAllChildren(int i, long j, struct linkedList * wll, int depth){
    removeRec(i+1, 2*j, wll, depth);
    removeRec(i+1, 2*j+1, wll, depth);
}

void removeRec(int i, long j, struct linkedList * wll, int depth){
    short res = searchAndRemove(pow(2, i)+j-1, wll);
    if (i >= depth){
        return;
    }
    removeRec(i+1, 2*j, wll, depth);
    removeRec(i+1, 2*j+1, wll, depth);
}

short cascadeRec(int i, long j, struct node * tree, struct linkedList * wll, int depth){
    long idx = pow(2, i)+j-1;
    if (tree[idx].val == 0){
        return 0;
    }
    if (i == depth){
        insertLL(idx, wll);
        return 1;
    }
    if (i % 2 == 0){
        short leftRes  = cascadeRec(i+1, 2*j, tree, wll, depth);
        short rightRes = cascadeRec(i+1, 2*j+1, tree, wll, depth);
        if (leftRes || rightRes){
            insertLL(idx, wll);
        }
        else{
            removeAllChildren(i, j, wll, depth);
        }
        return leftRes || rightRes;
    }
    else{
        short leftRes  = cascadeRec(i+1, 2*j, tree, wll, depth);
        short rightRes = cascadeRec(i+1, 2*j+1, tree, wll, depth);
        if (leftRes && rightRes){
            insertLL(idx, wll);
        }
        else{
            removeAllChildren(i, j, wll, depth);
        }
        return leftRes && rightRes;
    }
}

short winRec(int, long, struct node *, int);

/*
 Return whether Aaron can win, nothing else.
 */
short canWin(struct node * tree, int depth){
    return winRec(0, 0, tree, depth);
}

short winRec(int i, long j, struct node * tree, int depth){
    long idx = pow(2, i)+j-1;
    if (tree[idx].val == 0)
        return 0;
    if (i == depth)
        return 1;
    if (i % 2 == 0)
        return winRec(i+1, 2*j, tree, depth) || winRec(i+1, 2*j+1, tree, depth);
    else
        return winRec(i+1, 2*j, tree, depth) && winRec(i+1, 2*j+1, tree, depth);
}

/*
 Simulate the probability Aaron wins for finite depth.
 */
void simulateProb(int depth, double p, long iter){
    long wins = 0;
    for (int i = 0; i < iter; i++){
        struct node * tree = makeTree(p, depth);
        wins += canWin(tree, depth);
    }
    printf("W(p = %.6f, d = %2i) = %.30f\n", p, depth, wins/(double)iter);
}

/*
 Use the recurrence relation to calculate the exact probability Aaron wins for a finite-depth game
 */
void allRecurrenceProb(int depth, double p){
    double lX = 1, lY = 1, X, Y;
    for (int i = 1; i <= depth; i++){
        X = 2*p*lY-p*p*lY*lY;
        Y = p*p*lX*lX;
        lX = X;
        lY = Y;
        printf("W(p = %.6f, de = %2i) = %.15f\n", p, i, X);
    }
}

/*
 Check whether the probability that Aaron wins reaches a positive, nonzero steady state for a given p.
 */
short seeifSteadies(double p, long cutoffIter, long checkIter){
    double lA = 1, lB = 1, A, B; //lA stands for last A (as in previous)
    long counter = 0;
    while (counter < cutoffIter){
        counter++;
        A = 2*p*lB-p*p*lB*lB;
        B = p*p*lA*lA;
        lA = A;
        lB = B;
        if (counter % checkIter == 0){
            printf("depth, A = %25li %.75f\n", counter, A);
            printf("depth, B = %25li %.75f\n\n", counter, B);
        }
        if (!(A > 0)){
            printf("probability of winnig collapsed to zero at depth = %li\n", counter);
            return 0;
        }
    }
    return 1;
}

void compareSimulatedRecurrenceAndExplicitProb(double p, long simulateIter, int maxDepth){
    printf("Simulated Probabilities\n");
    for (int i = 1; i <= maxDepth; i++){
        simulateProb(i, p, simulateIter);
    }
    printf("Recurrence Probabilities\n");
    allRecurrenceProb(maxDepth, p);
    printf("First Few Explicit Probabilities Via Expanded Equations\n");
    printf("depth = 1: %.10f\n", 2*pow(p, 1) - pow(p, 2));
    printf("depth = 2: %.10f\n", 2*pow(p, 3)-pow(p, 6));
    printf("depth = 3: %.10f\n", -pow(p, 14)+8*pow(p, 13)-24*pow(p, 12)+32*pow(p, 11)-16*pow(p, 10)+2*pow(p, 7)-8*pow(p, 6)+8*pow(p, 5));
    printf("depth = 4: %.10f\n", -pow(p, 30)+8*pow(p, 27)-24*pow(p, 24)+32*pow(p, 21)-16*pow(p, 18)+2*pow(p, 15)-8*pow(p, 12)+8*pow(p, 9));
}

void simulateAndPrintWinningTrees(double p, long simulateIter, int maxDepth){
        double runningAvg = 0;
        int count = 0;
        for (int i = 0; i < simulateIter; i++){
            struct node * tree = makeTree(p, maxDepth);
            struct linkedList * cas = winningCascade(tree, maxDepth);
            short AaronWins = canWin(tree, maxDepth);
            if (AaronWins != (cas != NULL ? 1 : 0)){
                printf("Somehow winningCascade and canWin conflict, which would be very disturbing, and by that I mean a lot of debugging would be necessary...\nAborting...\n");
                break;
            }
            if (AaronWins){
                int numberOfEdgesInWinningCascade = lengthOfLL(cas);
                runningAvg = ((double)numberOfEdgesInWinningCascade + count*runningAvg)/(count + 1);
                count++;
                printBTree(maxDepth, tree, cas, 0);
                //printLL(cas); //prints indices that are part of the winning cascade
            }
        }
        printf("Simulated W(p = %.6f) = %.8f\n", p, count/(double)simulateIter);
        printf("Depth      = %i\n", maxDepth);
        printf("Iterations = %li\n", simulateIter);
        printf("Average number of nodes in winning casacde = %3.5f\n", runningAvg);
}

int main(int argc, char** argv){
    initRandom();
    
    /*
     Compare simulated and exact probabilities (from formulas) for finite depth and p = p1.
     */
    double p1 = .5;
    long simulateIter1 = 1000000;
    int maxDepth1 = 7;
    printf("COMPARING\n");
    compareSimulatedRecurrenceAndExplicitProb(p1, simulateIter1, maxDepth1);
    printf("\n\n");
    
    /*
     Find exact probabilities of Aaron winnin for finite depth 1, 2, and 3 via brute force.
     
     This counts by brute force the number of trees (up to labeling) where Aaron wins for finite depth
     (passed in as argument).
     This number divided by the total number of possible trees (up to labeling) is equal to the probability
     that Aaron wins when p = 1/2 since each labeling is equally likely.
     This approach is the worst because you need to check a nested exponential number of possible trees.
     For depth n = 4, there are 2^(4+1)-2 = 30 edges, which results in 2^30 different trees to check
     (excluding reductions that might come about from considering symmetry)
     For depth n = 5, there are 2^(5+1)-2 = 62 edges, which results in 2^62 different
     trees to check (wowza).
     */
    printf("BRUTE FORCE:\n");
    bruteForceWinningOrientations(1);
    bruteForceWinningOrientations(2);
    bruteForceWinningOrientations(3);
    printf("\n\n");
    /*
     This uses the recurrence relation for the probability that Aaron wins to check whether Aaron's
     probability of winning eventually steadies to a positive, nonzero value. Of course because of
     the imprecisions with how the numbers are expressed here, we cannot be 100% sure that the behavior
     this results in is accurate. However, bizarrely (if you haven't already worked out some of the math),
     this function shows us that for p < .944940787421154 Aaron's probability of winning eventually
     goes to zero (after hundreds of millions of rounds, mind you), but if we go above that value,
     say, with p = .944940787421155, then Aaron's probability of winning stops changing and remains
     ~0.8888889 for ... billions ... of rounds---so we have good reason to suspect that there's something
     special about this number, and, indeed, there is.
     */
    double p2 = .9449407874211547;
    printf("STEADY STATE CHECK\n");
    printf("p = %.20f\n", p2);
    seeifSteadies(p2, 10000000000, 1000000000);
    printf("\n\n");

    /*
     This also simulates probabilities but, more valuably (for me anyway), it actually prints out the
     game trees where Aaron wins. Granted, this did not direclty illuminate anything about how to solve
     the problem, but I found it very satisfying to actually see what the game trees look like when Aaron
     wind. Who knows, maybe my subconscious found it helpful.
     */
    double p3 = .80;
    long simulateIter2 = 100;
    int maxDepth2 = 6; 
    printf("DRAW WINNING TREES\n");
    simulateAndPrintWinningTrees(p3, simulateIter2, maxDepth2);
    printf("\n\n");

    double p = 3 * pow(2, -5/(double)3); // (final answer)    
    
    return 0;
}
