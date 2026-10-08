# 🏆 Event Sourcing for a game
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import json

# 🎯 Base event class
class Event(ABC):
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.timestamp = datetime.now()
        self.version = 1
    
    @abstractmethod
    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass

# 🎮 Game events
class GameStartedEvent(Event):
    def __init__(self, player_id: str, player_name: str):
        super().__init__(player_id)
        self.player_name = player_name
        self.emoji = "🎮"
    
    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **state,
            'player_id': self.aggregate_id,
            'player_name': self.player_name,
            'score': 0,
            'level': 1,
            'achievements': ["🌟 First Steps"],
            'status': 'playing'
        }

class PointsEarnedEvent(Event):
    def __init__(self, player_id: str, points: int):
        super().__init__(player_id)
        self.points = points
        self.emoji = "✨"
    
    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        new_score = state['score'] + self.points
        new_level = (new_score // 100) + 1
        
        new_state = {
            **state,
            'score': new_score,
            'level': new_level
        }
        
        # 🎊 Level up achievement
        if new_level > state['level']:
            new_state['achievements'] = state['achievements'] + [f"🏆 Level {new_level} Master"]
        
        return new_state

class PowerUpCollectedEvent(Event):
    def __init__(self, player_id: str, power_up: str):
        super().__init__(player_id)
        self.power_up = power_up
        self.emoji = "💪"
    
    def apply(self, state: Dict[str, Any]) -> Dict[str, Any]:
        power_ups = state.get('power_ups', [])
        return {
            **state,
            'power_ups': power_ups + [self.power_up]
        }

# 📚 Event store
class EventStore:
    def __init__(self):
        self._events: Dict[str, List[Event]] = {}
        print("💾 Event store initialized!")
    
    def save_event(self, event: Event):
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        
        # Set version number
        event.version = len(self._events[event.aggregate_id]) + 1
        self._events[event.aggregate_id].append(event)
        
        print(f"{getattr(event, 'emoji', '📝')} Event saved: {event.__class__.__name__} v{event.version}")
    
    def get_events(self, aggregate_id: str) -> List[Event]:
        return self._events.get(aggregate_id, [])

# 🎮 Game aggregate
class GamePlayer:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self._state: Dict[str, Any] = {}
    
    def start_game(self, player_id: str, player_name: str):
        event = GameStartedEvent(player_id, player_name)
        self.event_store.save_event(event)
        print(f"🎮 {player_name} started playing!")
    
    def earn_points(self, player_id: str, points: int):
        event = PointsEarnedEvent(player_id, points)
        self.event_store.save_event(event)
        
        # Get current state to show level up
        state = self.get_player_state(player_id)
        print(f"✨ Earned {points} points! Score: {state['score']}")
    
    def collect_power_up(self, player_id: str, power_up: str):
        event = PowerUpCollectedEvent(player_id, power_up)
        self.event_store.save_event(event)
        print(f"💪 Collected power-up: {power_up}")
    
    def get_player_state(self, player_id: str) -> Dict[str, Any]:
        # Rebuild state from events
        events = self.event_store.get_events(player_id)
        state = {}
        
        for event in events:
            state = event.apply(state)
        
        return state
    
    def replay_game_history(self, player_id: str):
        print(f"\n🎬 Replaying game history for player {player_id}:")
        events = self.event_store.get_events(player_id)
        
        state = {}
        for i, event in enumerate(events):
            state = event.apply(state)
            print(f"  📹 Event {i+1}: {event.__class__.__name__} - Score: {state.get('score', 0)}")

# 🎮 Let's play!
event_store = EventStore()
game = GamePlayer(event_store)

# Start a new game
game.start_game("player-1", "Alice")

# Play the game
game.earn_points("player-1", 50)
game.collect_power_up("player-1", "🚀 Speed Boost")
game.earn_points("player-1", 75)
game.collect_power_up("player-1", "🛡️ Shield")
game.earn_points("player-1", 100)

# Check final state
final_state = game.get_player_state("player-1")
print(f"\n📊 Final state: Level {final_state['level']}, Score: {final_state['score']}")
print(f"🏆 Achievements: {', '.join(final_state['achievements'])}")
print(f"💪 Power-ups: {', '.join(final_state.get('power_ups', []))}")

# Replay history
game.replay_game_history("player-1")