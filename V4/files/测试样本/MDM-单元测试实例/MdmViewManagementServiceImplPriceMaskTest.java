package com.sunny.modules.mdmviewmanagement.service.impl;

import com.sunny.modules.mdmviewmanagement.BaseTest;
import com.sunny.modules.mdmviewmanagement.dao.MdmViewAllMapper;
import com.sunny.modules.mdmviewmanagement.entity.MdmViewAccounting;
import com.sunny.modules.mdmviewmanagement.entity.MdmViewAll;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.math.BigDecimal;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

public class MdmViewManagementServiceImplPriceMaskTest extends BaseTest {

    @Mock
    private MdmViewAllMapper mdmViewAllMapper;

    @InjectMocks
    private MdmViewManagementServiceImpl service;

    @Test
    public void isPriceMasked_withRole_returnsTrue() {
        when(mdmViewAllMapper.check_per(any(MdmViewAll.class))).thenReturn(1);
        assertTrue(service.isPriceMasked("612497"));
    }

    @Test
    public void isPriceMasked_withoutRole_returnsFalse() {
        when(mdmViewAllMapper.check_per(any(MdmViewAll.class))).thenReturn(0);
        assertFalse(service.isPriceMasked("612497"));
    }

    @Test
    public void isPriceMasked_nullUsernumb_returnsFalse() {
        assertFalse(service.isPriceMasked(null));
    }

    @Test
    public void maskAccountingPrice_setsBothPricesToZero() {
        MdmViewAccounting accounting = new MdmViewAccounting();
        accounting.setnYdpjj(new BigDecimal("15.5"));
        accounting.setnBzjg(new BigDecimal("20.0"));
        service.maskAccountingPrice(accounting);
        assertEquals(0, BigDecimal.ZERO.compareTo(accounting.getnYdpjj()));
        assertEquals(0, BigDecimal.ZERO.compareTo(accounting.getnBzjg()));
    }

    @Test
    public void maskAccountingPrice_nullEntity_noException() {
        service.maskAccountingPrice(null);
    }
}
