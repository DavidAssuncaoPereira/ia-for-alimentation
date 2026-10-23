import React, { useState, useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useNavigation } from '@react-navigation/native';
import { Scan, X, Camera as CameraIcon } from 'lucide-react-native';
import { analyzeMeal } from '../api/client';
import { useMealStore } from '../store/useMealStore';
import CameraOverlay from '../components/CameraOverlay';

export default function ScannerScreen() {
  const navigation = useNavigation<any>();
  const [permission, requestPermission] = useCameraPermissions();
  const [isBarcodeMode, setIsBarcodeMode] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const cameraRef = useRef<CameraView>(null);
  const plateDiameterCm = useMealStore((state) => state.plateDiameterCm);

  useEffect(() => {
    if (!permission?.granted) {
      requestPermission();
    }
  }, [permission]);

  const takePicture = async () => {
    if (cameraRef.current && !isProcessing) {
      setIsProcessing(true);
      try {
        const photo = await cameraRef.current.takePictureAsync({ quality: 0.8 });

        if (isBarcodeMode) {
          // Handle Barcode via API
          // For now, we reuse the meal analysis structure conceptually, or navigate to a specific flow
          Alert.alert("Barcode Mode", "Barcode scan via image API called.");
          setIsProcessing(false);
        } else {
          // Send to ML backend
          const result = await analyzeMeal(photo.uri, plateDiameterCm);

          navigation.replace('AnalysisResult', {
            imageUri: photo.uri,
            analysisResult: result
          });
        }
      } catch (error: any) {
        setIsProcessing(false);
        Alert.alert("Error", error.message || "Failed to analyze meal.");
      }
    }
  };

  if (!permission) return <View style={styles.container} />;
  if (!permission.granted) return <Text>No access to camera</Text>;

  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} facing="back" ref={cameraRef}>

        {!isBarcodeMode && <CameraOverlay plateDiameterCm={plateDiameterCm} />}

        <View style={styles.topBar}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.iconBtn}>
            <X color="#fff" size={28} />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => setIsBarcodeMode(!isBarcodeMode)} style={styles.modeToggle}>
            {isBarcodeMode ? <CameraIcon color="#fff" size={20} /> : <Scan color="#fff" size={20} />}
            <Text style={styles.modeText}>{isBarcodeMode ? 'Food Mode' : 'Barcode Mode'}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.bottomBar}>
          <TouchableOpacity
            style={styles.captureButton}
            onPress={takePicture}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ActivityIndicator color="#000" />
            ) : (
              <View style={styles.captureInner} />
            )}
          </TouchableOpacity>
        </View>

      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  topBar: {
    position: 'absolute',
    top: 50,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    zIndex: 10,
  },
  iconBtn: {
    padding: 8,
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: 20,
  },
  modeToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  modeText: {
    color: '#fff',
    marginLeft: 8,
    fontWeight: 'bold',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 40,
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 10,
  },
  captureButton: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureInner: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#fff',
  }
});
