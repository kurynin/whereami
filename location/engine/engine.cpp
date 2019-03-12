#include <fstream>
#include <string>

using namespace std;

int main(int argc, char *argv[]) {
    (void)argc;

    ifstream inIni(argv[1]);

    string str;
    string gga = ".gga";
    string rtk = ".rtk";

    inIni >> str >> str >> str;

    ifstream inFile(str.c_str());

    inIni >> str >> str >> str;

    ifstream inTopconInfo(str.c_str());

    inIni >> str >> str >> str;

    string tmp = str + argv[2] + gga;
    ofstream outResult(tmp.c_str());
    tmp = str + argv[2] + rtk;
    ofstream outStat(tmp.c_str());

    int A, B, C, X = 1;

    inIni >> str >> str >> C;
    inFile >> A;
    inTopconInfo >> B;

    outResult << A * X * X + B * X + C << "\n";
    outStat << "A = " << A << " B = " << B << " C = " << C << "\n";

    return 0;
}

