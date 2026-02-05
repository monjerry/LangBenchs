#include <random>

int main() {
    std::mt19937_64 rng(42);
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    int inside = 0;
    int n = 10'000'000;
    for (int i = 0; i < n; i++) {
        double x = dist(rng);
        double y = dist(rng);
        if (x * x + y * y <= 1.0) inside++;
    }
    return 0;
}
