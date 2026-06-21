# Complete Project Architecture

This document contains the complete, detailed computation graph of the Arena Battle Robot Game, mapping out every node, topic namespace, and connection in the system.

## Complete Computation Graph

```mermaid
graph TD
    subgraph Lobby ["Discovery & Lobby"]
        LA["/lobby_advertisement\nDiscovery & sync"]
        LJ["/lobby_join_request\nJoin requests"]
    end

    subgraph GameServer ["Game Server"]
        MS(["/game_server\nMaster coordinator"])
        WS(["/game_server_m######\nMatch worker"])
        MS -->|spawns| WS

        subgraph MatchTopics ["Match Topics"]
            P1C["/match/m######/p1/command"]
            P2C["/match/m######/p2/command"]
            GS["/match/m######/game_state"]
        end
    end

    subgraph Clients ["Player Clients"]
        P1(["/p1/pygame_node\nHost / P1"])
        P2(["/p2/pygame_node\nGuest / P2"])
    end

    LA -->|triggers spawn| MS
    P1 <-->|pub/sub JSON| LA
    P2 <-->|pub/sub JSON| LA
    P2 -->|publish join request| LJ
    LJ --> P1

    P1 -->|publish controls| P1C
    P2 -->|publish controls| P2C
    P1C --> WS
    P2C --> WS
    WS -->|publish @ 100Hz| GS
    GS -.->|subscribe for rendering| P1
    GS -.->|subscribe for rendering| P2
```

For simplified, isolated views of these components, refer to:
* **[Game Server Architecture](game_server_architecture.md)**
* **[Lobby Discovery & Matchmaking Flow](lobby_discovery.md)**
* **[Gameplay Match Communication Flow](match_gameplay.md)**
