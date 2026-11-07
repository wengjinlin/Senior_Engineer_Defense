package com.sunny.modules.mdmviewmanagement.service.impl;

import org.junit.Before;
import org.junit.Test;

import java.lang.reflect.Method;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertSame;
import static org.junit.Assert.assertTrue;

/**
 * MdmViewManagementAutoServiceImpl.trimDataMap 工具方法单元测试。
 * 被测方法为 private，通过反射调用。
 */
public class MdmViewManagementAutoServiceImplTrimTest {

    private Object service;
    private Method trimMethod;

    @Before
    public void setUp() throws Exception {
        service = new MdmViewManagementAutoServiceImpl();
        trimMethod = MdmViewManagementAutoServiceImpl.class.getDeclaredMethod(
                "trimDataMap", List.class);
        trimMethod.setAccessible(true);
    }

    private void invoke(List<Map<String, Object>> dataMap) throws Exception {
        trimMethod.invoke(service, dataMap);
    }

    @Test
    public void trim_string_value_removes_leading_and_trailing_whitespace() throws Exception {
        Map<String, Object> row = new HashMap<>();
        row.put("工厂", "  1600  ");
        row.put("物料编码", " A01");
        List<Map<String, Object>> dataMap = new ArrayList<>();
        dataMap.add(row);

        invoke(dataMap);

        assertEquals("1600", row.get("工厂"));
        assertEquals("A01", row.get("物料编码"));
    }

    @Test
    public void non_string_value_is_preserved() throws Exception {
        BigDecimal num = new BigDecimal("3.14");
        Date date = new Date();
        Map<String, Object> row = new HashMap<>();
        row.put("num", num);
        row.put("date", date);
        row.put("nullVal", null);
        List<Map<String, Object>> dataMap = new ArrayList<>();
        dataMap.add(row);

        invoke(dataMap);

        assertSame(num, row.get("num"));
        assertSame(date, row.get("date"));
        assertNull(row.get("nullVal"));
    }

    @Test
    public void empty_and_blank_string_become_empty() throws Exception {
        Map<String, Object> row = new HashMap<>();
        row.put("empty", "");
        row.put("blank", "   ");
        List<Map<String, Object>> dataMap = new ArrayList<>();
        dataMap.add(row);

        invoke(dataMap);

        assertEquals("", row.get("empty"));
        assertEquals("", row.get("blank"));
    }

    @Test
    public void null_or_empty_datamap_is_safe() throws Exception {
        invoke(null);
        invoke(new ArrayList<Map<String, Object>>());

        List<Map<String, Object>> withNullRow = new ArrayList<>();
        withNullRow.add(null);
        invoke(withNullRow);
    }

    @Test
    public void map_key_is_not_modified() throws Exception {
        Map<String, Object> row = new HashMap<>();
        row.put("工厂 ", "  1600  ");
        List<Map<String, Object>> dataMap = new ArrayList<>();
        dataMap.add(row);

        invoke(dataMap);

        assertTrue(row.containsKey("工厂 "));
        assertFalse(row.containsKey("工厂"));
        assertEquals("1600", row.get("工厂 "));
    }
}
