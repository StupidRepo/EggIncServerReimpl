# `src/utils/`
## Hashing
The game uses 2 versions of hashing, to prevent cheating and hacking.
As this is a server re-implementation, and I'm aiming to be as close to the original as possible, I have implemented the hashing algorithm used in the game.

However... you will need to implement the hashing algorithm yourself, as I do not want to provide it in this repository.
Here's some pointers to help you implement it:
- Both versions of the hashing algorithm use SHA256.
- Ghidra/IDA Pro is your friend.

After you've figured it out, create a file called `hashing.ts`, with these methods:
```ts
// Both functions are expected to return a hex string of the SHA256 hash.

export function hash_v1(input: Uint8Array): string { return "..." }
export function hash_v2(input: Uint8Array): string { return "..." }
```