int global_var = 21;

int test(int n) {
    if (n>0) {
        return n;
    } else {
        return global_var - n;
    }
}
