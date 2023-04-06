#include <iostream>

// root
#include "TFile.h"
#include "TTree.h"
#include "ROOT/RDataFrame.hxx"

// nodes
struct node
{
    int index = 0;
    long int curIndex = 0;
    double time = -1;
    node* next = NULL;
};

struct treeList
{
    node* baseNode = NULL;
    node* pop() {
        node* thisNode = baseNode;
        baseNode = baseNode->next;
        return thisNode;
     };
    void add(node* newNode){
        node* nodePos = baseNode;
        // empty list
        if(nodePos == NULL){
            baseNode = newNode;
            return;
        }
        // shorter than the head node
        if(newNode->time < nodePos->time){
            baseNode = newNode;
            baseNode->next = nodePos;
            return;
        }
        // go through the node list
        while(nodePos != NULL){
            node* nextNode = nodePos->next;
            // if we're at the end of the list
            if(nextNode == NULL){
                nodePos->next = newNode;
                break;
            }

            // if we're shorter than the next node
            if(newNode->time < nextNode->time){
                nodePos->next = newNode;
                newNode->next = nextNode;
                std::cout << "new node!\n";
                break;
            }else{
                nodePos = nodePos->next;
            }
        }
    }; 
};

int main(int argc, char** argv)
{
    std::cout << "ni hao!\n";
    treeList tl;

    // add 5 nodes and test
    for(int i=0; i<5; i++){
        node* t = new node;
        t->time = 5 - i;
        tl.add(t);
    }

    // pop and print
    for(int i=0; i<5; i++){
        std::cout << "pop.. ";
        auto n = tl.pop();
        std::cout << "node " << i << ", is val: " << n->time << std::endl;
    }

    std::cout << "temp complete.\n";
    return 0;
}