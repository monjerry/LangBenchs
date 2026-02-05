// Xorshift64 PRNG — no external crates needed
struct Xorshift64 {
    state: u64,
}

impl Xorshift64 {
    fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    fn next_f64(&mut self) -> f64 {
        self.state ^= self.state << 13;
        self.state ^= self.state >> 7;
        self.state ^= self.state << 17;
        (self.state as f64) / (u64::MAX as f64)
    }
}

fn main() {
    let mut rng = Xorshift64::new(42);
    let mut inside: u64 = 0;
    let n: u64 = 10_000_000;
    for _ in 0..n {
        let x = rng.next_f64();
        let y = rng.next_f64();
        if x * x + y * y <= 1.0 {
            inside += 1;
        }
    }
}
