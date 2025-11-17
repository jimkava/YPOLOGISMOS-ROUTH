import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  SafeAreaView
} from 'react-native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RootStackParamList } from '../navigation/types';

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

export default function HomeScreen({ navigation }: Props) {
  const degrees = [1, 2, 3, 4, 5, 6];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.title}>ΥΠΟΛΟΓΙΣΜΟΣ ΕΥΣΤΑΘΕΙΑΣ</Text>
          <Text style={styles.subtitle}>ΜΕ ΤΗΝ ΜΕΘΟΔΟ ROUTH</Text>
          <Text style={styles.author}>ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc.</Text>
          <Text style={styles.authorTitle}>ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ</Text>
        </View>

        <View style={styles.menuContainer}>
          <Text style={styles.menuTitle}>ΜΕΝΟΥ ΕΠΙΛΟΓΗΣ ΧΕ</Text>

          {degrees.map((degree) => (
            <TouchableOpacity
              key={degree}
              style={styles.degreeButton}
              onPress={() => navigation.navigate('Calculator', { degree })}
            >
              <Text style={styles.degreeButtonText}>
                ΧΕ {degree}ου ΒΑΘΜΟΥ
              </Text>
            </TouchableOpacity>
          ))}
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
    padding: 20,
    borderRadius: 10,
    marginBottom: 30,
    alignItems: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ecf0f1',
    textAlign: 'center',
    marginBottom: 15,
  },
  author: {
    fontSize: 14,
    color: '#bdc3c7',
    textAlign: 'center',
  },
  authorTitle: {
    fontSize: 12,
    color: '#bdc3c7',
    textAlign: 'center',
  },
  menuContainer: {
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
  menuTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    marginBottom: 20,
  },
  degreeButton: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  degreeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
