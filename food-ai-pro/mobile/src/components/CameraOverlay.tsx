import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import Svg, { Circle, Defs, Mask, Rect } from 'react-native-svg';

interface CameraOverlayProps {
  plateDiameterCm: number;
}

export default function CameraOverlay({ plateDiameterCm }: CameraOverlayProps) {
  const { width, height } = Dimensions.get('window');

  // We draw a circle that visually represents the plate on the screen
  // Assuming a rough visual calibration where 26cm is ~80% of screen width
  const circleDiameter = (plateDiameterCm / 26.0) * (width * 0.8);
  const radius = circleDiameter / 2;
  const cx = width / 2;
  const cy = height / 2.5; // Slightly above center

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <Svg height="100%" width="100%">
        <Defs>
          <Mask id="mask">
            {/* Draw a white rectangle to make everything opaque */}
            <Rect x="0" y="0" width="100%" height="100%" fill="white" />
            {/* Draw a black circle to cut out the hole */}
            <Circle cx={cx} cy={cy} r={radius} fill="black" />
          </Mask>
        </Defs>
        <Rect
          x="0"
          y="0"
          width="100%"
          height="100%"
          fill="rgba(0,0,0,0.5)"
          mask="url(#mask)"
        />
        {/* Draw an outline for the plate guide */}
        <Circle cx={cx} cy={cy} r={radius} stroke="white" strokeWidth="2" strokeDasharray="10, 5" fill="transparent" />
      </Svg>
    </View>
  );
}
