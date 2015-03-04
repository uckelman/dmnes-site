<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

  <!-- identity transformation -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template> 

  <!-- match the CNF and VNF nodes which have freeform contents -->
  <xsl:template match="
      /cnf/etym//*
    | /cnf/def//*
    | /cnf/usg//*
    | /cnf/note//*
    | /vnf/place//*
    | /vnf/bibl/loc//*
    | /vnf/note//*
  ">
    <xsl:choose>
      <!-- copy HTML5 nodes as-is -->
      <xsl:when test="
             name() = 'a'
          or name() = 'abbr'
          or name() = 'address'
          or name() = 'area'
          or name() = 'article'
          or name() = 'aside'
          or name() = 'audio'
          or name() = 'b'
          or name() = 'base'
          or name() = 'bdi'
          or name() = 'bdo'
          or name() = 'blockquote'
          or name() = 'body'
          or name() = 'br'
          or name() = 'button'
          or name() = 'canvas'
          or name() = 'caption'
          or name() = 'cite'
          or name() = 'code'
          or name() = 'col'
          or name() = 'colgroup'
          or name() = 'data'
          or name() = 'datalist'
          or name() = 'dd'
          or name() = 'del'
          or name() = 'dfn'
          or name() = 'div'
          or name() = 'dl'
          or name() = 'dt'
          or name() = 'em'
          or name() = 'embed'
          or name() = 'fieldset'
          or name() = 'figcaption'
          or name() = 'figure'
          or name() = 'footer'
          or name() = 'form'
          or name() = 'h1'
          or name() = 'h2'
          or name() = 'h3'
          or name() = 'h4'
          or name() = 'h5'
          or name() = 'h6'
          or name() = 'head'
          or name() = 'header'
          or name() = 'hr'
          or name() = 'html'
          or name() = 'i'
          or name() = 'iframe'
          or name() = 'img'
          or name() = 'input'
          or name() = 'ins'
          or name() = 'kbd'
          or name() = 'keygen'
          or name() = 'label'
          or name() = 'legend'
          or name() = 'li'
          or name() = 'link'
          or name() = 'main'
          or name() = 'map'
          or name() = 'mark'
          or name() = 'meta'
          or name() = 'meter'
          or name() = 'nav'
          or name() = 'noscript'
          or name() = 'object'
          or name() = 'ol'
          or name() = 'optgroup'
          or name() = 'option'
          or name() = 'output'
          or name() = 'p'
          or name() = 'param'
          or name() = 'pre'
          or name() = 'progress'
          or name() = 'q'
          or name() = 'rb'
          or name() = 'rp'
          or name() = 'rt'
          or name() = 'rtc'
          or name() = 'ruby'
          or name() = 's'
          or name() = 'samp'
          or name() = 'script'
          or name() = 'section'
          or name() = 'select'
          or name() = 'small'
          or name() = 'source'
          or name() = 'span'
          or name() = 'strong'
          or name() = 'style'
          or name() = 'sub'
          or name() = 'sup'
          or name() = 'table'
          or name() = 'tbody'
          or name() = 'td'
          or name() = 'template'
          or name() = 'textarea'
          or name() = 'tfoot'
          or name() = 'th'
          or name() = 'thead'
          or name() = 'time'
          or name() = 'title'
          or name() = 'tr'
          or name() = 'track'
          or name() = 'u'
          or name() = 'ul'
          or name() = 'var'
          or name() = 'video'
          or name() = 'wbr'
      ">
        <xsl:copy>
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <!-- replace non-HTML5 nodes with spans -->
        <span class="{name()}"><xsl:apply-templates select="@*|node()"/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- replace all non-key bibl nodes with spans -->
  <xsl:template match="/bibl//*[not(name() = 'key')]">
    <span class="{name()}"><xsl:apply-templates select="@*|node()"/></span>
  </xsl:template>

</xsl:stylesheet>
