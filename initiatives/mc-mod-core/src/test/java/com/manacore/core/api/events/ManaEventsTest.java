package com.manacore.core.api.events;

import com.manacore.core.api.events.ManaFlowEvent;
import com.manacore.core.api.events.ManaGatherEvent;
import com.manacore.core.api.events.ManaStoreEvent;
import com.manacore.core.api.events.ManaStoreEvent.Operation;

/**
 * Executable tests for mana event records.
 * Tests validation rules and immutability.
 */
public class ManaEventsTest {
    
    public static void main(String[] args) {
        int passed = 0;
        int failed = 0;
        
        System.out.println("Running ManaEventsTest...");
        
        // Test ManaFlowEvent
        try {
            testManaFlowEventValid();
            testManaFlowEventInvalidAmount();
            testManaFlowEventInvalidDirection();
            passed += 3;
        } catch (Exception e) {
            System.err.println("ManaFlowEvent test failed: " + e.getMessage());
            failed++;
        }
        
        // Test ManaGatherEvent
        try {
            testManaGatherEventValid();
            testManaGatherEventInvalidRadius();
            testManaGatherEventInvalidAmount();
            passed += 3;
        } catch (Exception e) {
            System.err.println("ManaGatherEvent test failed: " + e.getMessage());
            failed++;
        }
        
        // Test ManaStoreEvent
        try {
            testManaStoreEventValid();
            testManaStoreEventBlankStorageId();
            testManaStoreEventNullStorageId();
            testManaStoreEventNullOperation();
            testManaStoreEventInvalidAmount();
            passed += 5;
        } catch (Exception e) {
            System.err.println("ManaStoreEvent test failed: " + e.getMessage());
            failed++;
        }
        
        // Test immutability
        try {
            testImmutability();
            passed += 1;
        } catch (Exception e) {
            System.err.println("Immutability test failed: " + e.getMessage());
            failed++;
        }
        
        System.out.println("Tests completed: " + passed + " passed, " + failed + " failed");
        
        if (failed > 0) {
            System.exit(1);
        }
    }
    
    // ManaFlowEvent tests
    private static void testManaFlowEventValid() {
        ManaFlowEvent event = new ManaFlowEvent(
            1, 2, 3, 4, 5, 6, 10.5, 1, 0, -1
        );
        assert event.sourceX() == 1;
        assert event.sourceY() == 2;
        assert event.sourceZ() == 3;
        assert event.targetX() == 4;
        assert event.targetY() == 5;
        assert event.targetZ() == 6;
        assert event.amount() == 10.5;
        assert event.directionX() == 1;
        assert event.directionY() == 0;
        assert event.directionZ() == -1;
    }
    
    private static void testManaFlowEventInvalidAmount() {
        boolean caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, -1.0, 0, 0, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative amount";
        
        caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, Double.POSITIVE_INFINITY, 0, 0, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject positive infinite amount";
        
        caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, Double.NEGATIVE_INFINITY, 0, 0, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative infinite amount";
        
        caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, Double.NaN, 0, 0, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject NaN amount";
    }
    
    private static void testManaFlowEventInvalidDirection() {
        boolean caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, 1.0, 2, 0, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject directionX > 1";
        
        caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, 1.0, 0, -2, 0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject directionY < -1";
        
        caught = false;
        try {
            new ManaFlowEvent(0, 0, 0, 1, 1, 1, 1.0, 0, 0, 5);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject directionZ > 1";
    }
    
    // ManaGatherEvent tests
    private static void testManaGatherEventValid() {
        ManaGatherEvent event = new ManaGatherEvent(1, 2, 3, 5, 20.0);
        assert event.centerX() == 1;
        assert event.centerY() == 2;
        assert event.centerZ() == 3;
        assert event.radius() == 5;
        assert event.amount() == 20.0;
    }
    
    private static void testManaGatherEventInvalidRadius() {
        boolean caught = false;
        try {
            new ManaGatherEvent(0, 0, 0, -1, 1.0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative radius";
    }
    
    private static void testManaGatherEventInvalidAmount() {
        boolean caught = false;
        try {
            new ManaGatherEvent(0, 0, 0, 5, -1.0);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative amount";
        
        caught = false;
        try {
            new ManaGatherEvent(0, 0, 0, 5, Double.POSITIVE_INFINITY);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject positive infinite amount";
        
        caught = false;
        try {
            new ManaGatherEvent(0, 0, 0, 5, Double.NEGATIVE_INFINITY);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative infinite amount";
        
        caught = false;
        try {
            new ManaGatherEvent(0, 0, 0, 5, Double.NaN);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject NaN amount";
    }
    
    // ManaStoreEvent tests
    private static void testManaStoreEventValid() {
        ManaStoreEvent event = new ManaStoreEvent("storage1", 15.0, Operation.INSERT);
        assert event.storageId().equals("storage1");
        assert event.amount() == 15.0;
        assert event.operation() == Operation.INSERT;
        
        event = new ManaStoreEvent("storage2", 5.0, Operation.EXTRACT);
        assert event.storageId().equals("storage2");
        assert event.amount() == 5.0;
        assert event.operation() == Operation.EXTRACT;
    }
    
    private static void testManaStoreEventBlankStorageId() {
        boolean caught = false;
        try {
            new ManaStoreEvent("", 1.0, Operation.INSERT);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject blank storageId";
        
        caught = false;
        try {
            new ManaStoreEvent("   ", 1.0, Operation.INSERT);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject whitespace storageId";
    }
    
    private static void testManaStoreEventNullStorageId() {
        boolean caught = false;
        try {
            new ManaStoreEvent(null, 1.0, Operation.INSERT);
        } catch (NullPointerException e) {
            caught = true;
        }
        assert caught : "Should reject null storageId";
    }
    
    private static void testManaStoreEventNullOperation() {
        boolean caught = false;
        try {
            new ManaStoreEvent("storage1", 1.0, null);
        } catch (NullPointerException e) {
            caught = true;
        }
        assert caught : "Should reject null operation";
    }
    
    private static void testManaStoreEventInvalidAmount() {
        boolean caught = false;
        try {
            new ManaStoreEvent("storage1", -1.0, Operation.INSERT);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative amount";
        
        caught = false;
        try {
            new ManaStoreEvent("storage1", Double.POSITIVE_INFINITY, Operation.INSERT);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject positive infinite amount";
        
        caught = false;
        try {
            new ManaStoreEvent("storage1", Double.NEGATIVE_INFINITY, Operation.INSERT);
        } catch (IllegalArgumentException e) {
            caught = true;
        }
        assert caught : "Should reject negative infinite amount";
    }
    
    // Immutability tests
    private static void testImmutability() {
        ManaFlowEvent flowEvent = new ManaFlowEvent(1, 2, 3, 4, 5, 6, 10.0, 1, 0, -1);
        ManaGatherEvent gatherEvent = new ManaGatherEvent(1, 2, 3, 5, 20.0);
        ManaStoreEvent storeEvent = new ManaStoreEvent("storage1", 15.0, Operation.INSERT);
        
        // Records are immutable by design - just verify they can be created
        // and their accessor methods work
        assert flowEvent.sourceX() == 1;
        assert gatherEvent.radius() == 5;
        assert storeEvent.storageId().equals("storage1");
    }
}
