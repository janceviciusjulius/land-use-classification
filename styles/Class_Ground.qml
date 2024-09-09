<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="0" minScale="1e+08" version="3.24.2-Tisler" styleCategories="AllStyleCategories" maxScale="0">
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
      <Option type="bool" name="WMSBackgroundLayer" value="false"/>
      <Option type="bool" name="WMSPublishDataSourceUrl" value="false"/>
      <Option type="int" name="embeddedWidgets/count" value="0"/>
      <Option type="QString" name="identify/format" value="Value"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" name="name" value=""/>
      <Option name="properties"/>
      <Option type="QString" name="type" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour" enabled="false" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer opacity="1" nodataColor="" band="1" alphaBand="-1" type="paletted">
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
        <paletteEntry label="Cultivated_meadows" color="#935d07" alpha="255" value="11"/>
        <paletteEntry label="Decay" color="#4a3903" alpha="255" value="12"/>
        <paletteEntry label="Stubble" color="#acca16" alpha="255" value="13"/>
        <paletteEntry label="Winter cereals" color="#0de718" alpha="255" value="14"/>
        <paletteEntry label="Intermediate crops" color="#4fb284" alpha="255" value="15"/>
        <paletteEntry label="Intensive cultivated crops" color="#d7ff0d" alpha="255" value="16"/>
        <paletteEntry label="Natural meadows" color="#3ba12e" alpha="255" value="21"/>
        <paletteEntry label="Forest" color="#156801" alpha="255" value="31"/>
        <paletteEntry label="Stagnant water" color="#101fc9" alpha="255" value="41"/>
        <paletteEntry label="Wetland" color="#066576" alpha="255" value="43"/>
        <paletteEntry label="Urban areas" color="#840aff" alpha="255" value="51"/>
        <paletteEntry label="Sand dune" color="#c7b10c" alpha="255" value="61"/>
        <paletteEntry label="Peatland" color="#de181b" alpha="255" value="62"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0" gamma="1"/>
    <huesaturation colorizeGreen="128" colorizeBlue="128" grayscaleMode="0" colorizeRed="255" colorizeStrength="100" saturation="0" invertColors="0" colorizeOn="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
