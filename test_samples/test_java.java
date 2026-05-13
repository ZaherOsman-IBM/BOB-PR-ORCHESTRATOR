/**
 * Arquivo de teste Java com problemas propositais
 */

package com.ibm.test;

import java.util.*;

// ❌ Classe com nome errado (deve começar com maiúscula)
public class myTestClass {
    
    // ❌ Senha hardcoded
    private static final String password = "senha123";
    private static final String API_KEY = "AKIAIOSFODNN7EXAMPLE";
    
    // ❌ Constante com nome errado (deve ser UPPER_SNAKE_CASE)
    private static final String apiEndpoint = "https://api.example.com";
    
    // ❌ Método muito longo (> 30 linhas)
    public void processData(List<String> data) {
        for (String item : data) {
            System.out.println(item);
        }
        
        // Muitas linhas...
        int a = 1;
        int b = 2;
        int c = 3;
        int d = 4;
        int e = 5;
        int f = 6;
        int g = 7;
        int h = 8;
        int i = 9;
        int j = 10;
        int k = 11;
        int l = 12;
        int m = 13;
        int n = 14;
        int o = 15;
        int p = 16;
        int q = 17;
        int r = 18;
        int s = 19;
        int t = 20;
        int u = 21;
        int v = 22;
        int w = 23;
        int x = 24;
        int y = 25;
        int z = 26;
    }
    
    // ❌ Catch genérico
    public void readFile(String path) {
        try {
            // código
        } catch (Exception e) {
            // ❌ Catch vazio
        }
    }
    
    // ❌ Uso de API deprecated
    public void useOldDate() {
        Date date = new Date();
        Vector vector = new Vector();
        Hashtable table = new Hashtable();
    }
    
    // ❌ Loop que poderia ser Stream
    public List<Integer> doubleNumbers(List<Integer> numbers) {
        List<Integer> result = new ArrayList<>();
        for (Integer num : numbers) {
            result.add(num * 2);
        }
        return result;
    }
    
    // ❌ Retorna null sem @Nullable
    public String findUser(int id) {
        if (id < 0) {
            return null;
        }
        return "User" + id;
    }
    
    // ✅ Método correto
    public List<Integer> doubleNumbersCorrect(List<Integer> numbers) {
        return numbers.stream()
            .map(n -> n * 2)
            .collect(Collectors.toList());
    }
}

// Made with Bob
