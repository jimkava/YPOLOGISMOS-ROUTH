import { RouthResult, Coefficients } from '../utils/routhCalculator';

export type RootStackParamList = {
  Home: undefined;
  Calculator: {
    degree: number;
  };
  Results: {
    result: RouthResult;
    degree: number;
    coefficients: Coefficients;
  };
};
