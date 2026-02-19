package com.example.dice.service;

import com.example.dice.model.Dice;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.Random;
import java.util.concurrent.atomic.AtomicInteger;

import io.micrometer.core.instrument.Counter;

@Service
public class DiceService {

    private final Random random = new Random();
    private final AtomicInteger rollCounter = new AtomicInteger(0);
    private final Counter diceRollsMetric;

    public DiceService(MeterRegistry registry) {
        this.diceRollsMetric = Counter.builder("dice_rolls_total")
                .description("Total number of dice rolls")
                .register(registry);
    }

    public Dice rollDice() {
        int number = random.nextInt(6) + 1;
        long id = System.currentTimeMillis();
        rollCounter.incrementAndGet();
        diceRollsMetric.increment();
        return Dice.builder().id(id).number(number).build();
    }

    public int getCounter() {
        return rollCounter.get();
    }

    public boolean isHealthy() {
        File logDir = new File("/var/log/dice/application.log");
        return logDir.exists() && logDir.canWrite();
    }
}