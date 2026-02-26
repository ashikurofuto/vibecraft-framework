# Sequence Diagrams: Asteroids Game

**Version:** 1.0  
**Status:** Accepted  
**Last Updated:** 2026-02-25

---

## 📋 Overview

Этот документ описывает последовательности взаимодействий для критических сценариев игры.

---

## 🎮 Game Startup Sequence

```mermaid
sequenceDiagram
    participant User
    participant HTML as index.html
    participant JS as index.js
    participant Game as Game
    participant GL as GameLoop
    participant GS as GameState
    participant R as Renderer
    participant IH as InputHandler
    participant UI as UIController

    User->>HTML: Open page
    HTML->>JS: Load script
    JS->>Game: new Game()
    Game->>GS: new GameState()
    Game->>GL: new GameLoop()
    Game->>R: new Renderer(canvas)
    Game->>IH: new InputHandler()
    Game->>UI: new UIController()
    
    JS->>Game: initialize()
    Game->>GS: state = 'menu'
    Game->>R: loadAssets()
    R-->>Game: Assets ready
    
    JS->>Game: start()
    Game->>GL: start()
    GL->>Game: tick(timestamp)
    
    Note over Game,UI: Show Menu Screen
    Game->>UI: renderMenu()
    UI-->>User: Display Menu
```

---

## 🚀 Game Loop Sequence (Per Frame)

```mermaid
sequenceDiagram
    participant GL as GameLoop
    participant G as Game
    participant IH as InputHandler
    participant GS as GameState
    participant SH as Ship
    participant AS as Asteroids
    participant BU as Bullets
    participant CD as CollisionDetector
    participant SM as ScoreManager
    participant R as Renderer
    participant UI as UIController

    loop Every Frame (60 FPS)
        GL->>G: tick(currentTime)
        
        G->>IH: getInput()
        IH-->>G: InputState
        
        G->>GS: isPlaying()?
        GS-->>G: true/false
        
        alt isPlaying()
            G->>SH: update(deltaTime)
            G->>AS: update(deltaTime)
            G->>BU: update(deltaTime)
            
            G->>IH: wasFirePressed()?
            IH-->>G: true
            G->>SH: fire()
            SH-->>G: Bullet
            
            G->>CD: checkAll(entities)
            CD-->>G: Collision[]
            
            loop For each collision
                G->>G: handleCollision()
                G->>SM: addScore(points)
            end
            
            G->>GS: checkLevelComplete()
            GS-->>G: nextLevel?
        end
        
        G->>R: render(entities)
        G->>UI: updateHUD(score, lives)
    end
```

---

## 🔫 Player Fires Bullet Sequence

```mermaid
sequenceDiagram
    participant User
    participant KB as Keyboard
    participant IH as InputHandler
    participant G as Game
    participant SH as Ship
    participant BP as BulletPool
    participant BU as Bullet
    participant AU as AudioController

    User->>KB: Press Space
    KB->>IH: keydown event (Space)
    IH->>IH: keys.add('Space')
    
    Note over G: Next game tick
    
    G->>IH: wasFirePressed()?
    IH-->>G: true
    
    G->>SH: canFire()?
    SH-->>G: true (cooldown ready)
    
    G->>SH: fire()
    SH->>SH: getMuzzlePosition()
    SH->>SH: getVelocity()
    SH->>BP: acquire()
    BP->>BU: reset()
    BU->>BU: position = muzzlePosition
    BU->>BU: velocity = shipVelocity + bulletSpeed
    BP-->>SH: Bullet
    SH-->>G: Bullet created
    
    G->>AU: playShoot()
    AU-->>User: Pew! sound
```

---

## 💥 Asteroid Destruction Sequence

```mermaid
sequenceDiagram
    participant BU as Bullet
    participant AS as Asteroid
    participant CD as CollisionDetector
    participant G as Game
    participant SM as ScoreManager
    participant AS_Factory as AsteroidFactory
    participant AU as AudioController
    participant R as Renderer

    Note over BU,AS: Collision detected
    BU->>CD: getCollisionBox()
    AS->>CD: getCollisionBox()
    CD->>CD: intersects()?
    CD-->>G: true (bullet-asteroid)
    
    G->>AS: getSize()
    AS-->>G: 'large' | 'medium' | 'small'
    
    alt size === 'large'
        G->>SM: addScore(20)
        G->>AS_Factory: createAsteroid(position, 'medium')
        AS_Factory-->>G: Asteroid #1
        G->>AS_Factory: createAsteroid(position, 'medium')
        AS_Factory-->>G: Asteroid #2
        G->>AS: markForDeletion()
    else size === 'medium'
        G->>SM: addScore(50)
        G->>AS_Factory: createAsteroid(position, 'small')
        AS_Factory-->>G: Asteroid #1
        G->>AS_Factory: createAsteroid(position, 'small')
        AS_Factory-->>G: Asteroid #2
        G->>AS: markForDeletion()
    else size === 'small'
        G->>SM: addScore(100)
        G->>AS: markForDeletion()
    end
    
    G->>AU: playExplosion()
    AU-->>User: Boom! sound
    
    G->>R: renderExplosion(position)
    R-->>User: Draw explosion effect
```

---

## 💀 Ship Death Sequence

```mermaid
sequenceDiagram
    participant SH as Ship
    participant AS as Asteroid
    participant CD as CollisionDetector
    participant G as Game
    participant GS as GameState
    participant SM as ScoreManager
    participant AU as AudioController
    participant UI as UIController

    Note over SH,AS: Collision detected
    SH->>CD: getCollisionBox()
    AS->>CD: getCollisionBox()
    CD->>CD: intersects()?
    CD-->>G: true (ship-asteroid)
    
    G->>GS: decrementLives()
    GS-->>G: lives (2, 1, or 0)
    
    G->>AU: playExplosion()
    AU-->>User: Boom! sound
    
    alt lives > 0
        G->>SH: resetPosition()
        G->>SH: resetVelocity()
        G->>SH: resetRotation()
        G->>UI: updateLives(lives)
        Note over G: Respawn after delay
    else lives === 0
        G->>GS: gameOver()
        G->>SM: getCurrentScore()
        SM-->>G: score
        G->>SM: isHighScore(score)?
        SM-->>G: true/false
        alt isHighScore
            G->>SM: saveHighScore(score)
        end
        G->>UI: showGameOver(score)
        UI-->>User: Game Over screen
    end
```

---

## ⏸️ Pause/Resume Sequence

```mermaid
sequenceDiagram
    participant User
    participant KB as Keyboard
    participant IH as InputHandler
    participant G as Game
    participant GL as GameLoop
    participant GS as GameState
    participant UI as UIController

    User->>KB: Press P
    KB->>IH: keydown event (KeyP)
    IH->>IH: keys.add('KeyP')
    
    G->>IH: wasPausePressed()?
    IH-->>G: true
    
    G->>GS: getState()
    GS-->>G: 'playing' | 'paused'
    
    alt state === 'playing'
        G->>GS: pause()
        GS-->>G: state = 'paused'
        G->>GL: stop()
        G->>UI: showPauseMenu()
        UI-->>User: Display Pause screen
    else state === 'paused'
        G->>GS: resume()
        GS-->>G: state = 'playing'
        G->>GL: start()
        G->>UI: hidePauseMenu()
        UI-->>User: Resume game
    end
```

---

## 🏆 High Score Save Sequence

```mermaid
sequenceDiagram
    participant G as Game
    participant SM as ScoreManager
    participant ST as Storage
    participant LS as localStorage
    participant UI as UIController

    G->>GS: isGameOver()?
    GS-->>G: true
    
    G->>SM: getCurrentScore()
    SM-->>G: score
    
    G->>SM: getHighScore()
    SM-->>G: highScore
    
    alt score > highScore
        G->>SM: saveHighScore(score)
        SM->>ST: saveHighScore(score)
        ST->>LS: setItem('asteroids-highscore', JSON)
        LS-->>ST: saved
        ST-->>SM: success
        SM-->>G: new high score!
        G->>UI: showNewHighScore(score)
        UI-->>User: "New High Score!" message
    else score <= highScore
        G->>UI: showGameOver(score)
        UI-->>User: Game Over screen
    end
```

---

## 🎯 Level Complete Sequence

```mermaid
sequenceDiagram
    participant G as Game
    participant AS as Asteroids
    participant GS as GameState
    participant SM as ScoreManager
    participant UI as UIController
    participant AS_Factory as AsteroidFactory

    G->>AS: countAlive()
    AS-->>G: 0 (all destroyed)
    
    G->>GS: nextLevel()
    GS-->>G: level++
    
    G->>GS: getAsteroidCount(level)
    GS-->>G: count (base + level * 2)
    
    loop For each asteroid to spawn
        G->>AS_Factory: createAsteroid(randomPos, 'large')
        AS_Factory-->>G: Asteroid
        G->>AS: add(asteroid)
    end
    
    G->>UI: showLevelComplete(level)
    UI-->>User: "Level X" message
    
    Note over G: Game continues with more asteroids
```

---

## 🌌 Hyperspace Sequence

```mermaid
sequenceDiagram
    participant User
    participant KB as Keyboard
    participant IH as InputHandler
    participant G as Game
    participant SH as Ship
    participant M as Math.random()
    participant AU as AudioController

    User->>KB: Press H
    KB->>IH: keydown event (KeyH)
    IH->>IH: keys.add('KeyH')
    
    G->>IH: wasHyperspacePressed()?
    IH-->>G: true
    
    G->>SH: activateHyperspace()
    SH->>M: random()
    M-->>SH: 0.0 - 1.0
    
    alt random < 0.1 (10% risk)
        SH-->>G: died (spawned in asteroid)
        G->>AU: playExplosion()
        G->>GS: decrementLives()
    else random >= 0.1
        SH->>SH: newPosition = random position
        SH-->>G: teleported
        G->>AU: playWarpSound()
        AU-->>User: Warp sound
    end
```

---

## 🎨 Render Sequence (Detailed)

```mermaid
sequenceDiagram
    participant G as Game
    participant R as Renderer
    participant C as Canvas Context
    participant SH as Ship
    participant AS as Asteroids
    participant BU as Bullets
    participant UF as UFOs

    G->>R: render(gameState)
    
    R->>C: clearRect(0, 0, width, height)
    R->>C: fillStyle = '#000000'
    R->>C: fillRect(0, 0, width, height)
    
    R->>C: strokeStyle = '#FFFFFF'
    R->>C: lineWidth = 2
    
    R->>SH: getVertices()
    SH-->>R: [v1, v2, v3]
    R->>SH: getPosition()
    SH-->>R: Vector2D
    R->>SH: getRotation()
    SH-->>R: angle
    R->>C: save()
    R->>C: translate(x, y)
    R->>C: rotate(angle)
    R->>C: beginPath()
    R->>C: moveTo(v1)
    R->>C: lineTo(v2)
    R->>C: lineTo(v3)
    R->>C: closePath()
    R->>C: stroke()
    R->>C: restore()
    
    loop For each asteroid
        R->>AS: getVertices()
        AS-->>R: [v1, v2, ...]
        R->>C: drawPolygon(vertices)
    end
    
    loop For each bullet
        R->>BU: getPosition()
        BU-->>R: Vector2D
        R->>C: drawLine(position, direction)
    end
    
    loop For each UFO
        R->>UF: getVertices()
        UF-->>R: [ellipse params]
        R->>C: drawUFO(vertices)
    end
```

---

## 📥 Input Handling Sequence (Detailed)

```mermaid
sequenceDiagram
    participant User
    participant KB as Keyboard
    participant IH as InputHandler
    participant G as Game
    participant SH as Ship

    Note over IH: At game start
    IH->>IH: keys = new Set()
    IH->>KB: addEventListener('keydown')
    IH->>KB: addEventListener('keyup')
    
    User->>KB: Press ArrowUp
    KB->>IH: keydown (ArrowUp)
    IH->>IH: keys.add('ArrowUp')
    
    User->>KB: Press ArrowLeft
    KB->>IH: keydown (ArrowLeft)
    IH->>IH: keys.add('ArrowLeft')
    
    Note over G: During game tick
    G->>IH: isPressed('ArrowUp')
    IH-->>G: true
    G->>SH: thrust()
    
    G->>IH: isPressed('ArrowLeft')
    IH-->>G: true
    G->>SH: rotate(-1)
    
    User->>KB: Release ArrowUp
    KB->>IH: keyup (ArrowUp)
    IH->>IH: keys.delete('ArrowUp')
    
    G->>IH: isPressed('ArrowUp')
    IH-->>G: false
    Note over SH: Stop thrusting
```

---

## 🔄 Entity Update Sequence (Physics)

```mermaid
sequenceDiagram
    participant G as Game
    participant SH as Ship
    participant AS as Asteroid
    participant BU as Bullet
    participant V2D as Vector2D

    Note over G: Fixed timestep update (1/60s)
    
    G->>SH: update(deltaTime)
    SH->>V2D: velocity * deltaTime
    V2D-->>SH: displacement
    SH->>SH: position += displacement
    SH->>SH: applyFriction(0.99)
    SH->>SH: wrapPosition()
    
    G->>AS: update(deltaTime)
    AS->>V2D: velocity * deltaTime
    V2D-->>AS: displacement
    AS->>AS: position += displacement
    AS->>AS: wrapPosition()
    
    G->>BU: update(deltaTime)
    BU->>V2D: velocity * deltaTime
    V2D-->>BU: displacement
    BU->>BU: position += displacement
    BU->>BU: lifetime -= deltaTime
    BU->>BU: isAlive = lifetime > 0
```

---

**Sequence Diagrams Status:** ✅ Accepted  
**Design Phase:** Complete  
**Next Phase:** Plan (Implementation Planning)  
**Architect Agent:** Complete
