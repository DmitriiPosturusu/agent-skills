package com.example.dice;

import com.example.dice.model.Dice;
import com.example.dice.service.DiceService;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

public class DiceServiceTest {

    @Test
    void testDiceRollIsBetween1And6() {
        DiceService diceService = new DiceService(new SimpleMeterRegistry());

        for (int i = 0; i < 100; i++) { // roll multiple times
            Dice dice = diceService.rollDice();
            int number = dice.getNumber();

            assertTrue(number >= 1 && number <= 6,
                    "Dice roll out of range: " + number);
        }
    }
}
