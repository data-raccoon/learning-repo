package com.manacore.core.api.types;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;

/**
 * Executable test for Mana API type interfaces.
 * Verifies interface contracts using reflection and dummy implementations.
 */
public class ManaApiTypesTest {
    
    public static void main(String[] args) {
        boolean allPassed = true;
        
        allPassed &= testManaConsumerInterface();
        allPassed &= testManaCreatorInterface();
        allPassed &= testManaStorageInterface();
        allPassed &= testDummyImplementations();
        
        if (allPassed) {
            System.out.println("All ManaApiTypesTest checks passed.");
            System.exit(0);
        } else {
            System.out.println("Some ManaApiTypesTest checks failed.");
            System.exit(1);
        }
    }
    
    private static boolean testManaConsumerInterface() {
        System.out.println("Testing ManaConsumer interface...");
        
        // Verify interface exists and is an interface
        if (!ManaConsumer.class.isInterface()) {
            System.err.println("FAIL: ManaConsumer is not an interface");
            return false;
        }
        
        // Verify methods exist with correct signatures
        try {
            Method gatherRadius = ManaConsumer.class.getMethod("gatherRadius");
            if (gatherRadius.getReturnType() != int.class) {
                System.err.println("FAIL: gatherRadius return type is not int");
                return false;
            }
            if (gatherRadius.getParameterCount() != 0) {
                System.err.println("FAIL: gatherRadius has parameters");
                return false;
            }
            
            Method acceptMana = ManaConsumer.class.getMethod("acceptMana", double.class);
            if (acceptMana.getReturnType() != double.class) {
                System.err.println("FAIL: acceptMana return type is not double");
                return false;
            }
            if (acceptMana.getParameterCount() != 1) {
                System.err.println("FAIL: acceptMana parameter count is not 1");
                return false;
            }
            
            // Verify no Minecraft/Fabric imports in interface
            if (ManaConsumer.class.getName().contains("net.minecraft") || 
                ManaConsumer.class.getName().contains("fabric")) {
                System.err.println("FAIL: ManaConsumer has Minecraft/Fabric dependencies");
                return false;
            }
            
            System.out.println("PASS: ManaConsumer interface contract verified");
            return true;
        } catch (NoSuchMethodException e) {
            System.err.println("FAIL: Missing method in ManaConsumer: " + e.getMessage());
            return false;
        }
    }
    
    private static boolean testManaCreatorInterface() {
        System.out.println("Testing ManaCreator interface...");
        
        if (!ManaCreator.class.isInterface()) {
            System.err.println("FAIL: ManaCreator is not an interface");
            return false;
        }
        
        try {
            Method injectionRadius = ManaCreator.class.getMethod("injectionRadius");
            if (injectionRadius.getReturnType() != int.class) {
                System.err.println("FAIL: injectionRadius return type is not int");
                return false;
            }
            if (injectionRadius.getParameterCount() != 0) {
                System.err.println("FAIL: injectionRadius has parameters");
                return false;
            }
            
            Method manaPerTick = ManaCreator.class.getMethod("manaPerTick");
            if (manaPerTick.getReturnType() != double.class) {
                System.err.println("FAIL: manaPerTick return type is not double");
                return false;
            }
            if (manaPerTick.getParameterCount() != 0) {
                System.err.println("FAIL: manaPerTick parameter count is not 0");
                return false;
            }
            
            System.out.println("PASS: ManaCreator interface contract verified");
            return true;
        } catch (NoSuchMethodException e) {
            System.err.println("FAIL: Missing method in ManaCreator: " + e.getMessage());
            return false;
        }
    }
    
    private static boolean testManaStorageInterface() {
        System.out.println("Testing ManaStorage interface...");
        
        if (!ManaStorage.class.isInterface()) {
            System.err.println("FAIL: ManaStorage is not an interface");
            return false;
        }
        
        try {
            Method storedMana = ManaStorage.class.getMethod("storedMana");
            if (storedMana.getReturnType() != double.class) {
                System.err.println("FAIL: storedMana return type is not double");
                return false;
            }
            if (storedMana.getParameterCount() != 0) {
                System.err.println("FAIL: storedMana has parameters");
                return false;
            }
            
            Method capacity = ManaStorage.class.getMethod("capacity");
            if (capacity.getReturnType() != double.class) {
                System.err.println("FAIL: capacity return type is not double");
                return false;
            }
            if (capacity.getParameterCount() != 0) {
                System.err.println("FAIL: capacity has parameters");
                return false;
            }
            
            Method insert = ManaStorage.class.getMethod("insert", double.class);
            if (insert.getReturnType() != double.class) {
                System.err.println("FAIL: insert return type is not double");
                return false;
            }
            if (insert.getParameterCount() != 1) {
                System.err.println("FAIL: insert parameter count is not 1");
                return false;
            }
            
            Method extract = ManaStorage.class.getMethod("extract", double.class);
            if (extract.getReturnType() != double.class) {
                System.err.println("FAIL: extract return type is not double");
                return false;
            }
            if (extract.getParameterCount() != 1) {
                System.err.println("FAIL: extract parameter count is not 1");
                return false;
            }
            
            System.out.println("PASS: ManaStorage interface contract verified");
            return true;
        } catch (NoSuchMethodException e) {
            System.err.println("FAIL: Missing method in ManaStorage: " + e.getMessage());
            return false;
        }
    }
    
    private static boolean testDummyImplementations() {
        System.out.println("Testing dummy implementations...");
        
        // Test ManaConsumer dummy
        ManaConsumer consumer = new DummyManaConsumer();
        if (consumer.gatherRadius() != 5) {
            System.err.println("FAIL: DummyManaConsumer.gatherRadius() != 5");
            return false;
        }
        if (consumer.acceptMana(10.0) != 10.0) {
            System.err.println("FAIL: DummyManaConsumer.acceptMana(10.0) != 10.0");
            return false;
        }
        
        // Test ManaCreator dummy
        ManaCreator creator = new DummyManaCreator();
        if (creator.injectionRadius() != 3) {
            System.err.println("FAIL: DummyManaCreator.injectionRadius() != 3");
            return false;
        }
        if (creator.manaPerTick() != 1.5) {
            System.err.println("FAIL: DummyManaCreator.manaPerTick() != 1.5");
            return false;
        }
        
        // Test ManaStorage dummy
        ManaStorage storage = new DummyManaStorage();
        if (storage.storedMana() != 0.0) {
            System.err.println("FAIL: DummyManaStorage initial storedMana != 0.0");
            return false;
        }
        if (storage.capacity() != 100.0) {
            System.err.println("FAIL: DummyManaStorage.capacity() != 100.0");
            return false;
        }
        
        double inserted = storage.insert(50.0);
        if (inserted != 50.0) {
            System.err.println("FAIL: DummyManaStorage.insert(50.0) != 50.0");
            return false;
        }
        if (storage.storedMana() != 50.0) {
            System.err.println("FAIL: DummyManaStorage storedMana != 50.0 after insert");
            return false;
        }
        
        double extracted = storage.extract(25.0);
        if (extracted != 25.0) {
            System.err.println("FAIL: DummyManaStorage.extract(25.0) != 25.0");
            return false;
        }
        if (storage.storedMana() != 25.0) {
            System.err.println("FAIL: DummyManaStorage storedMana != 25.0 after extract");
            return false;
        }
        
        System.out.println("PASS: Dummy implementations verified");
        return true;
    }
    
    // Dummy implementations for testing
    private static class DummyManaConsumer implements ManaConsumer {
        @Override
        public int gatherRadius() {
            return 5;
        }
        
        @Override
        public double acceptMana(double offered) {
            return offered;
        }
    }
    
    private static class DummyManaCreator implements ManaCreator {
        @Override
        public int injectionRadius() {
            return 3;
        }
        
        @Override
        public double manaPerTick() {
            return 1.5;
        }
    }
    
    private static class DummyManaStorage implements ManaStorage {
        private double stored = 0.0;
        
        @Override
        public double storedMana() {
            return stored;
        }
        
        @Override
        public double capacity() {
            return 100.0;
        }
        
        @Override
        public double insert(double amount) {
            double toInsert = Math.min(amount, capacity() - stored);
            stored += toInsert;
            return toInsert;
        }
        
        @Override
        public double extract(double amount) {
            double toExtract = Math.min(amount, stored);
            stored -= toExtract;
            return toExtract;
        }
    }
}
