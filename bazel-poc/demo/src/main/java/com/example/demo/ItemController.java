package com.example.demo;

import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/items")
@CrossOrigin(origins = "http://localhost:3000")
public class ItemController {

    private List<Item> items = Arrays.asList(
            new Item(1L, "Spring Boot Service", "Java-based microservice"),
            new Item(2L, "Bazel Build", "Multi-language build tool"),
            new Item(3L, "Monorepo", "Single repository structure")
    );

    @GetMapping
    public List<Item> getAllItems() {
        return items;
    }

    @GetMapping("/{id}")
    public Item getItem(@PathVariable Long id) {
        return items.stream()
                .filter(item -> item.getId().equals(id))
                .findFirst()
                .orElse(null);
    }
}
