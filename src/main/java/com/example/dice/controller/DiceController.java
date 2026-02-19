package com.example.dice.controller;

import com.example.dice.model.Dice;
import com.example.dice.service.DiceService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;


@RestController
@Slf4j
public class DiceController {
    private final DiceService diceService;

    public DiceController(DiceService diceService) {
        this.diceService = diceService;
    }


    @GetMapping("/health")
    public ResponseEntity<String> health() {
        if (diceService.isHealthy()) {
            return ResponseEntity.ok("Service is healthy");
        } else {
            return ResponseEntity.status(500).body("Service not ready");
        }
    }

    @GetMapping("/healthfailure")
    public ResponseEntity<String> healthTest() {
        return ResponseEntity.status(500).body("Simulated failure");
    }

    @GetMapping("/dice")
    public String rollDice() {
        Dice dice = diceService.rollDice();
        log.info("Roll Dice: {}", dice);
        return "Dice thrown at " + dice.getId() + " with number: " + dice.getNumber();
    }

    @GetMapping("/counter")
    public int getCounter() {
        return diceService.getCounter();
    }
}
