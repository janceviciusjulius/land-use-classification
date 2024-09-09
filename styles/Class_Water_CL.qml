<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" minScale="1e+08" version="3.24.2-Tisler">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal mode="0" enabled="0" fetchMode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="bool" value="false" name="WMSBackgroundLayer"/>
      <Option type="bool" value="false" name="WMSPublishDataSourceUrl"/>
      <Option type="int" value="0" name="embeddedWidgets/count"/>
      <Option type="QString" value="Value" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" value="" name="name"/>
      <Option name="properties"/>
      <Option type="QString" value="collection" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer type="paletted" opacity="1" alphaBand="-1" nodataColor="" band="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry color="#6fb22c" value="5" label="5 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#75a92b" value="10" label="10 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#7aa129" value="15" label="15 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#809828" value="20" label="20 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#869026" value="25" label="25 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#8c8725" value="30" label="30 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#917f23" value="35" label="35 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#977622" value="40" label="40 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#9d6e20" value="45" label="45 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#a3651f" value="50" label="50 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#a85c1d" value="55" label="55 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#ae541c" value="60" label="60 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#b44b1a" value="65" label="65 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#ba4319" value="70" label="70 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#bf3a17" value="75" label="75 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#c53216" value="80" label="80 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#cb2914" value="85" label="85 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#d12113" value="90" label="90 µg Chl a/L" alpha="255"/>
        <paletteEntry color="#1117d6" value="101" label="Vegetation grasslands in water bodies" alpha="255"/>
        <paletteEntry color="#dc10c4" value="102" label="Wetland" alpha="255"/>
      </colorPalette>
      <colorramp type="gradient" name="[source]">
        <Option type="Map">
          <Option type="QString" value="111,178,44,255" name="color1"/>
          <Option type="QString" value="220,16,16,255" name="color2"/>
          <Option type="QString" value="ccw" name="direction"/>
          <Option type="QString" value="0" name="discrete"/>
          <Option type="QString" value="gradient" name="rampType"/>
          <Option type="QString" value="rgb" name="spec"/>
        </Option>
        <prop k="color1" v="111,178,44,255"/>
        <prop k="color2" v="220,16,16,255"/>
        <prop k="direction" v="ccw"/>
        <prop k="discrete" v="0"/>
        <prop k="rampType" v="gradient"/>
        <prop k="spec" v="rgb"/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeOn="0" grayscaleMode="0" colorizeStrength="100" invertColors="0" colorizeRed="255" colorizeGreen="128" colorizeBlue="128" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
