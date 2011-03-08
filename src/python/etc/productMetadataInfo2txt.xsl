<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
<xsl:output method="text" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:template match="productMetadataInfo">
      <xsl:choose>
          <xsl:when test="@code = '0'">
                    <xsl:apply-templates/>
          </xsl:when>
          <xsl:otherwise>
Unable to retrieve product description. Error is:
<xsl:value-of select="@msg"/>
          </xsl:otherwise>
      </xsl:choose>
  </xsl:template>
  <xsl:template match="timeCoverage">
- Time coverage:
  . begin: <xsl:value-of select="@start"/>
  . end:<xsl:value-of select="@end"/>      
  </xsl:template>

  <xsl:template match="geospatialCoverage">
- Depth range (in <xsl:value-of select="@depthUnits"/>):
  . min: <xsl:value-of select="@depthMin"/>
  . max:<xsl:value-of select="@depthMax"/>      
  </xsl:template>

 <xsl:template match="dataGeospatialCoverage">
- Geographic coverage:
  . longitude: [<xsl:value-of select="axis[@name='longitude']/@lower"/>, <xsl:value-of select="axis[@name='longitude']/@upper"/>]
  . latitude: [<xsl:value-of select="axis[@name='latitude']/@lower"/>, <xsl:value-of select="axis[@name='latitude']/@upper"/>]
 </xsl:template>

<xsl:template match="variables">
- Variables:<xsl:for-each select="variable">
  . <xsl:value-of select="@standardName"/>: <xsl:value-of select="@description"/> 
</xsl:for-each>
</xsl:template>    
   <xsl:template match="text()">    
   </xsl:template>

</xsl:stylesheet>
