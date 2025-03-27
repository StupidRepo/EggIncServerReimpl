# NeoInc
An Egg, Inc. server re-implementation, made in Python.

## Implementation Status
For fine details, see the [PROGRESS.md](/PROGRESS.md) file.

- [ ] Basic login
  - [ ] Session handling
  - [x] Actual account creation
  - [x] Backup saving & loading

- [ ] Configs
  - [x] Regular (see `utils.make_liveconfig()`)
  - [ ] Artifacts

- [ ] Periodicals
  - [x] Events
  - [ ] Missions
  - [ ] Contracts
  - [ ] Daily rewards

- [ ] Contracts
  - [ ] Making coops
  - [ ] Joining coops
  - [ ] Rewards
  - [ ] Gifting

## Usage
### Running the server
1. Clone the repository
2. Install the required dependencies with `pip` (`pip install Flask protobuf`)
3. Make a `.env` with a `MONGO_URI` for MongoDB.
4. Run the server with `python main.py`
### Connecting to the server
You can make the game use this server by either:
- Modifying the game's code to use the server
  - This is quite advanced and I personally recommend you do not do this as then you disallow yourself from easily switching between the official server and this one.
- Using `mitmproxy` and the mitmproxy script located in `proxy/mitmproxy.py`
  - You will need to do extra setup to get this to work on Android. Not sure about iOS.
  - Android users *may* need to install `mitmproxy`'s CA certificate as a system CA cert (which requires root).

## Accounts
An NeoInc account uses a NID (NeoInc ID), which is slightly different from Egg, Inc.'s EID.
The difference is how the ID is calculated (similar format, different code to produce an ID).

## Events
Events are in this format, in the `events` DB collection:
```json5
{
  // mongo's _id has no effect on the event ID. you need to specify the event ID in 'identifier'
  "identifier": "event-3-27",
  "seconds_remaining": 0, // leave this blank, it'll be filled automatically
  "type": "hab-sale", // unsure what other types there are
  "multiplier": 0.2, // 1 - 0.2 = 0.8 = 80%
  "subtitle": "80% OFF HEN HOUSES!",
  "start_time": 1743091200,
  "duration": 86400,
  "cc_only": false // cc = contract club, unused name for ultra. true if ultra only, false if everyone
}
```

They will be automatically deleted when `/ei/get_periodicals` is called and the event's seconds_remaining is 0.