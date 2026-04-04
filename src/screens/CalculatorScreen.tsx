import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  Alert,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';
import { calculateRouth, Coefficients } from '../utils/routhCalculator';

type Props = NativeStackScreenProps<RootStackParamList, 'Calculator'>;

export default function CalculatorScreen({ route, navigation }: Props) {
  const { degree } = route.params;
  const [coefficients, setCoefficients] = useState<Coefficients>({});
  const [kValue, setKValue] = useState<string>('');

  const getCoefficientFields = () => {
    const fields = [];
    for (let i = degree; i >= 1; i--) {
      fields.push(`a${i}`);
    }
    return fields;
  };

  const handleCoefficientChange = (key: string, value: string) => {
    setCoefficients({
      ...coefficients,
      [key]: value,
    });
  };

  const handleCalculate = () => {
    const fields = getCoefficientFields();
    const allCoefficients: Coefficients = {};

    // Validate all fields
    for (const field of fields) {
      const value = parseFloat(coefficients[field] || '0');
      if (isNaN(value)) {
        Alert.alert('Σφάλμα', `Παρακαλώ εισάγετε έγκυρη τιμή για ${field}`);
        return;
      }
      allCoefficients[field] = value;
    }

    // Add K value
    const k = parseFloat(kValue);
    if (isNaN(k)) {
      Alert.alert('Σφάλμα', 'Παρακαλώ εισάγετε έγκυρη τιμή για K');
      return;
    }
    allCoefficients.K = k;

    try {
      const result = calculateRouth(degree, allCoefficients);
      navigation.navigate('Results', { result, degree, coefficients: allCoefficients });
    } catch (error) {
      Alert.alert('Σφάλμα', 'Παρουσιάστηκε σφάλμα στον υπολογισμό');
    }
  };

  const getExponentText = (power: number): string => {
    const superscripts: { [key: number]: string } = {
      1: '¹',
      2: '²',
      3: '³',
      4: '⁴',
      5: '⁵',
      6: '⁶',
    };
    return superscripts[power] || `^${power}`;
  };

  const renderCharacteristicEquation = () => {
    const terms = [];
    for (let i = degree; i >= 1; i--) {
      const coeff = coefficients[`a${i}`] || `a${i}`;
      if (i === 1) {
        terms.push(`${coeff}s`);
      } else {
        terms.push(`${coeff}s${getExponentText(i)}`);
      }
    }
    terms.push('K');
    return terms.join(' + ') + ' = 0';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>ΧΕ {degree}ου ΒΑΘΜΟΥ</Text>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.sectionTitle}>Εισαγωγή Συντελεστών</Text>

          {getCoefficientFields().map((field) => (
            <View key={field} style={styles.inputGroup}>
              <Text style={styles.label}>{field}:</Text>
              <TextInput
                style={styles.input}
                keyboardType="numeric"
                placeholder={`Εισάγετε ${field}`}
                value={coefficients[field] || ''}
                onChangeText={(value) => handleCoefficientChange(field, value)}
              />
            </View>
          ))}

          <View style={styles.equationContainer}>
            <Text style={styles.equationLabel}>Χαρακτηριστική Εξίσωση:</Text>
            <Text style={styles.equation}>{renderCharacteristicEquation()}</Text>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>K:</Text>
            <TextInput
              style={styles.input}
              keyboardType="numeric"
              placeholder="Εισάγετε K"
              value={kValue}
              onChangeText={setKValue}
            />
          </View>

          <TouchableOpacity
            style={styles.calculateButton}
            onPress={handleCalculate}
          >
            <Text style={styles.calculateButtonText}>ΥΠΟΛΟΓΙΣΜΟΣ</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    backgroundColor: '#2c3e50',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
  },
  inputContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#34495e',
    marginBottom: 5,
  },
  input: {
    borderWidth: 1,
    borderColor: '#bdc3c7',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#ecf0f1',
  },
  equationContainer: {
    backgroundColor: '#ecf0f1',
    padding: 15,
    borderRadius: 8,
    marginVertical: 15,
  },
  equationLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#7f8c8d',
    marginBottom: 5,
  },
  equation: {
    fontSize: 16,
    color: '#2c3e50',
    fontFamily: 'monospace',
  },
  calculateButton: {
    backgroundColor: '#27ae60',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  calculateButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
