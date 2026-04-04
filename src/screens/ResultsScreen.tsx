import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView,
} from 'react-native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'Results'>;

export default function ResultsScreen({ route, navigation }: Props) {
  const { result, degree, coefficients } = route.params;

  const renderRouthTable = () => {
    return (
      <View style={styles.tableContainer}>
        <Text style={styles.tableTitle}>ΠΙΝΑΚΑΣ ROUTH</Text>
        {result.routhTable.map((row, rowIndex) => (
          <View key={rowIndex} style={styles.tableRow}>
            {row.map((cell, cellIndex) => (
              <View key={cellIndex} style={styles.tableCell}>
                <Text style={styles.tableCellText}>
                  {typeof cell === 'number' ? cell.toFixed(2) : cell}
                </Text>
              </View>
            ))}
          </View>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>ΑΠΟΤΕΛΕΣΜΑΤΑ</Text>
        </View>

        <View style={styles.equationContainer}>
          <Text style={styles.equationLabel}>Χαρακτηριστική Εξίσωση:</Text>
          <Text style={styles.equation}>{result.characteristicEquation}</Text>
        </View>

        {renderRouthTable()}

        <View style={[
          styles.resultContainer,
          result.isStable ? styles.stableContainer : styles.unstableContainer
        ]}>
          <Text style={styles.resultTitle}>
            {result.isStable ? '✓ ΕΥΣΤΑΘΕΣ' : '✗ ΑΣΤΑΘΕΣ'}
          </Text>
          <Text style={styles.resultMessage}>{result.message}</Text>

          {result.kCritical && (
            <View style={styles.criticalValues}>
              <Text style={styles.criticalText}>
                Κκρ = {result.kCritical.toFixed(2)}
              </Text>
              {result.omegaCritical && (
                <Text style={styles.criticalText}>
                  ωκρ = {result.omegaCritical.toFixed(2)} rad/s
                </Text>
              )}
            </View>
          )}
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.newCalculationButton}
            onPress={() => navigation.navigate('Calculator', { degree })}
          >
            <Text style={styles.buttonText}>ΝΕΑ ΤΙΜΗ K</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.homeButton}
            onPress={() => navigation.navigate('Home')}
          >
            <Text style={styles.buttonText}>ΑΡΧΙΚΗ</Text>
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
  equationContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
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
  tableContainer: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  tableTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    marginBottom: 15,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#ecf0f1',
    paddingVertical: 10,
  },
  tableCell: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 5,
  },
  tableCellText: {
    fontSize: 14,
    color: '#2c3e50',
    fontFamily: 'monospace',
  },
  resultContainer: {
    padding: 20,
    borderRadius: 10,
    marginBottom: 20,
  },
  stableContainer: {
    backgroundColor: '#d5f4e6',
    borderWidth: 2,
    borderColor: '#27ae60',
  },
  unstableContainer: {
    backgroundColor: '#fadbd8',
    borderWidth: 2,
    borderColor: '#e74c3c',
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  resultMessage: {
    fontSize: 16,
    textAlign: 'center',
    color: '#2c3e50',
  },
  criticalValues: {
    marginTop: 15,
    padding: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.5)',
    borderRadius: 8,
  },
  criticalText: {
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    marginVertical: 3,
    color: '#2c3e50',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 10,
  },
  newCalculationButton: {
    flex: 1,
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  homeButton: {
    flex: 1,
    backgroundColor: '#95a5a6',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
