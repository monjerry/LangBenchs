// Simple seeded PRNG (mulberry32)
function mulberry32(seed) {
    return function () {
        seed |= 0;
        seed = seed + 0x6D2B79F5 | 0;
        let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 17) >>> 0) / 4294967296;
    };
}

const rand = mulberry32(42);
let inside = 0;
const n = 10_000_000;
for (let i = 0; i < n; i++) {
    const x = rand();
    const y = rand();
    if (x * x + y * y <= 1.0) inside++;
}
