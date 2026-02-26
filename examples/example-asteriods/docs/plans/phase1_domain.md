# Phase 1: Domain Layer Implementation

**Status:** Pending  
**Duration:** 7 дней  
**Priority:** High  
**Dependencies:** None (первая фаза)

---

## 📋 Overview

Реализация доменного слоя — ядра игры. Все сущности чистые, без внешних зависимостей.

### Components

| Component | File | Tests |
|-----------|------|-------|
| Vector2D | `src/domain/value-objects/Vector2D.js` | `test/domain/Vector2D.test.js` |
| CollisionBox | `src/domain/value-objects/CollisionBox.js` | `test/domain/CollisionBox.test.js` |
| Ship | `src/domain/entities/Ship.js` | `test/domain/Ship.test.js` |
| Bullet | `src/domain/entities/Bullet.js` | `test/domain/Bullet.test.js` |
| Asteroid | `src/domain/entities/Asteroid.js` | `test/domain/Asteroid.test.js` |
| UFO | `src/domain/entities/UFO.js` | `test/domain/UFO.test.js` |
| CollisionDetector | `src/domain/services/CollisionDetector.js` | `test/domain/CollisionDetector.test.js` |

---

## 🎯 Tasks

### Task 1.1: Vector2D

**TDD Workflow:**

```javascript
// test/domain/Vector2D.test.js
describe('Vector2D', () => {
    test('should create vector with x and y', () => {
        const v = new Vector2D(3, 4);
        expect(v.x).toBe(3);
        expect(v.y).toBe(4);
    });

    test('should add two vectors', () => {
        const v1 = new Vector2D(1, 2);
        const v2 = new Vector2D(3, 4);
        const result = v1.add(v2);
        expect(result.x).toBe(4);
        expect(result.y).toBe(6);
    });

    test('should calculate magnitude', () => {
        const v = new Vector2D(3, 4);
        expect(v.magnitude()).toBe(5);
    });

    test('should normalize vector', () => {
        const v = new Vector2D(3, 4);
        const normalized = v.normalize();
        expect(normalized.magnitude()).toBeCloseTo(1);
    });

    test('should calculate distance between vectors', () => {
        const v1 = new Vector2D(0, 0);
        const v2 = new Vector2D(3, 4);
        expect(Vector2D.distance(v1, v2)).toBe(5);
    });
});
```

**Implementation:**

```javascript
// src/domain/value-objects/Vector2D.js
export class Vector2D {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    add(other) {
        return new Vector2D(this.x + other.x, this.y + other.y);
    }

    subtract(other) {
        return new Vector2D(this.x - other.x, this.y - other.y);
    }

    multiply(scalar) {
        return new Vector2D(this.x * scalar, this.y * scalar);
    }

    magnitude() {
        return Math.sqrt(this.x ** 2 + this.y ** 2);
    }

    normalize() {
        const mag = this.magnitude();
        if (mag === 0) return new Vector2D(0, 0);
        return new Vector2D(this.x / mag, this.y / mag);
    }

    static distance(a, b) {
        return Math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2);
    }
}
```

---

### Task 1.2: CollisionBox

**TDD Workflow:**

```javascript
// test/domain/CollisionBox.test.js
describe('CollisionBox', () => {
    test('should create collision box with center and radius', () => {
        const center = new Vector2D(10, 10);
        const box = new CollisionBox(center, 5);
        expect(box.center).toEqual(center);
        expect(box.radius).toBe(5);
    });

    test('should contain point inside', () => {
        const center = new Vector2D(0, 0);
        const box = new CollisionBox(center, 10);
        const point = new Vector2D(5, 5);
        expect(box.contains(point)).toBe(true);
    });

    test('should not contain point outside', () => {
        const center = new Vector2D(0, 0);
        const box = new CollisionBox(center, 5);
        const point = new Vector2D(10, 10);
        expect(box.contains(point)).toBe(false);
    });

    test('should intersect with another box', () => {
        const box1 = new CollisionBox(new Vector2D(0, 0), 10);
        const box2 = new CollisionBox(new Vector2D(15, 0), 10);
        expect(box1.intersects(box2)).toBe(true);
    });

    test('should not intersect when far apart', () => {
        const box1 = new CollisionBox(new Vector2D(0, 0), 5);
        const box2 = new CollisionBox(new Vector2D(20, 0), 5);
        expect(box1.intersects(box2)).toBe(false);
    });
});
```

---

### Task 1.3: Ship

**Key Methods to Test:**

```javascript
describe('Ship', () => {
    test('should create ship at center', () => {
        const ship = new Ship(400, 300);
        expect(ship.position.x).toBe(400);
        expect(ship.position.y).toBe(300);
    });

    test('should rotate left', () => {
        const ship = new Ship(400, 300);
        ship.rotate(-1); // counter-clockwise
        expect(ship.rotation).toBeGreaterThan(0);
    });

    test('should rotate right', () => {
        const ship = new Ship(400, 300);
        ship.rotate(1); // clockwise
        expect(ship.rotation).toBeLessThan(0);
    });

    test('should thrust forward', () => {
        const ship = new Ship(400, 300);
        ship.thrust();
        expect(ship.velocity.magnitude()).toBeGreaterThan(0);
    });

    test('should apply friction', () => {
        const ship = new Ship(400, 300);
        ship.thrust();
        ship.update(1/60);
        ship.applyFriction(0.99);
        expect(ship.velocity.magnitude()).toBeLessThan(ship.velocity.magnitude());
    });

    test('should wrap position when off screen', () => {
        const ship = new Ship(400, 300);
        ship.position.x = -10;
        ship.wrapPosition(800, 600);
        expect(ship.position.x).toBe(790);
    });

    test('should return collision box', () => {
        const ship = new Ship(400, 300);
        const box = ship.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });

    test('should fire bullet', () => {
        const ship = new Ship(400, 300);
        const bullet = ship.fire();
        expect(bullet).toBeInstanceOf(Bullet);
    });
});
```

---

### Task 1.4: Bullet

**Key Methods to Test:**

```javascript
describe('Bullet', () => {
    test('should create bullet at position', () => {
        const pos = new Vector2D(100, 100);
        const vel = new Vector2D(0, -400);
        const bullet = new Bullet(pos, vel);
        expect(bullet.position).toEqual(pos);
    });

    test('should update position over time', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        bullet.update(1/60);
        expect(bullet.position.y).toBeLessThan(0);
    });

    test('should die after lifetime', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        bullet.update(2.1); // 2.1 seconds > 2s lifetime
        expect(bullet.isAlive).toBe(false);
    });

    test('should return collision box', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        const box = bullet.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });
});
```

---

### Task 1.5: Asteroid

**Key Methods to Test:**

```javascript
describe('Asteroid', () => {
    test('should create large asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        expect(asteroid.size).toBe('large');
        expect(asteroid.getCollisionBox().radius).toBe(60);
    });

    test('should create medium asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'medium');
        expect(asteroid.size).toBe('medium');
        expect(asteroid.getCollisionBox().radius).toBe(30);
    });

    test('should create small asteroid', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'small');
        expect(asteroid.size).toBe('small');
        expect(asteroid.getCollisionBox().radius).toBe(15);
    });

    test('should split large into 2 medium', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'large');
        const children = asteroid.split();
        expect(children.length).toBe(2);
        expect(children[0].size).toBe('medium');
        expect(children[1].size).toBe('medium');
    });

    test('should split medium into 2 small', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'medium');
        const children = asteroid.split();
        expect(children.length).toBe(2);
        expect(children[0].size).toBe('small');
    });

    test('should not split small', () => {
        const asteroid = new Asteroid(new Vector2D(0, 0), 'small');
        const children = asteroid.split();
        expect(children.length).toBe(0);
    });

    test('should return points based on size', () => {
        expect(new Asteroid(new Vector2D(0, 0), 'large').getPoints()).toBe(20);
        expect(new Asteroid(new Vector2D(0, 0), 'medium').getPoints()).toBe(50);
        expect(new Asteroid(new Vector2D(0, 0), 'small').getPoints()).toBe(100);
    });
});
```

---

### Task 1.6: UFO

**Key Methods to Test:**

```javascript
describe('UFO', () => {
    test('should create large UFO', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        expect(ufo.pattern).toBe('large');
    });

    test('should create small UFO', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        expect(ufo.pattern).toBe('small');
    });

    test('should try to fire when cooldown ready', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        const bullet = ufo.tryFire();
        expect(bullet).toBeInstanceOf(Bullet);
    });

    test('should not fire when cooldown not ready', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'small');
        ufo.tryFire(); // fired once
        const bullet2 = ufo.tryFire(); // should be null
        expect(bullet2).toBeNull();
    });

    test('should return collision box', () => {
        const ufo = new UFO(new Vector2D(0, 0), 'large');
        const box = ufo.getCollisionBox();
        expect(box).toBeInstanceOf(CollisionBox);
    });

    test('should return points based on type', () => {
        expect(new UFO(new Vector2D(0, 0), 'large').getPoints()).toBe(200);
        expect(new UFO(new Vector2D(0, 0), 'small').getPoints()).toBe(1000);
    });
});
```

---

### Task 1.7: CollisionDetector

**Key Methods to Test:**

```javascript
describe('CollisionDetector', () => {
    test('should detect ship-asteroid collision', () => {
        const ship = new Ship(0, 0);
        const asteroid = new Asteroid(new Vector2D(5, 0), 'large');
        const collisions = CollisionDetector.checkShipAsteroid(ship, asteroid);
        expect(collisions.length).toBeGreaterThan(0);
    });

    test('should not detect collision when far apart', () => {
        const ship = new Ship(0, 0);
        const asteroid = new Asteroid(new Vector2D(200, 200), 'small');
        const collisions = CollisionDetector.checkShipAsteroid(ship, asteroid);
        expect(collisions.length).toBe(0);
    });

    test('should detect bullet-asteroid collision', () => {
        const bullet = new Bullet(new Vector2D(0, 0), new Vector2D(0, -400));
        const asteroid = new Asteroid(new Vector2D(0, 50), 'medium');
        const collisions = CollisionDetector.checkBulletAsteroid(bullet, asteroid);
        expect(collisions.length).toBeGreaterThan(0);
    });

    test('should detect ship-ufo collision', () => {
        const ship = new Ship(0, 0);
        const ufo = new UFO(new Vector2D(5, 0), 'large');
        const collisions = CollisionDetector.checkShipUFO(ship, ufo);
        expect(collisions.length).toBeGreaterThan(0);
    });

    test('should check all collisions at once', () => {
        const entities = {
            ship: new Ship(0, 0),
            asteroids: [new Asteroid(new Vector2D(5, 0), 'large')],
            bullets: [],
            ufos: []
        };
        const allCollisions = CollisionDetector.checkAll(entities);
        expect(allCollisions.length).toBeGreaterThan(0);
    });
});
```

---

## ✅ Definition of Done

- [ ] Все 7 модулей реализованы
- [ ] Все тесты написаны ДО кода (TDD)
- [ ] Покрытие тестами >90%
- [ ] Все тесты проходят: `npm test`
- [ ] Нет ESLint ошибок: `npm run lint`
- [ ] Domain слой без внешних зависимостей
- [ ] Код следует именованию (PascalCase для классов)
- [ ] JSDoc комментарии для публичных методов

---

## 📁 Files to Create

```
src/domain/
├── value-objects/
│   ├── Vector2D.js
│   └── CollisionBox.js
├── entities/
│   ├── Ship.js
│   ├── Bullet.js
│   ├── Asteroid.js
│   └── UFO.js
└── services/
    └── CollisionDetector.js

test/domain/
├── Vector2D.test.js
├── CollisionBox.test.js
├── Ship.test.js
├── Bullet.test.js
├── Asteroid.test.js
├── UFO.test.js
└── CollisionDetector.test.js
```

---

**Phase 1 Status:** Ready to Start  
**Next:** pre_checker validation → tdd_writer Task 1.1
