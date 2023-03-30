import React, { useContext } from "react";
import styles from './Sidebar.module.scss';
import {
  Accordion,
  AccordionItem,
  AccordionItemHeading,
  AccordionItemButton,
  AccordionItemPanel,
} from 'react-accessible-accordion';
import Checkbox from "../Checkbox/Checkbox";
import { capitalizeFirstLetter } from "../../Utilities/utilities";
import StoreContext from '../../Utilities/StoreContext';

const Sidebar = () => {
  const store = useContext(StoreContext);

  return (
    <div className={styles.sidebar}>
      <h5>Recent Benchmarks</h5>
      {
        store.sidebarLinks &&
        <Accordion
          allowZeroExpanded={true}
          className={styles.accordion}
          >
          {          
            Object.keys(store.sidebarLinks).map((benchmark, i)=>{
              return(
                <AccordionItem key={i} className={styles.accordionItem}>
                  <AccordionItemHeading className={styles.accordionHeading}>
                    <AccordionItemButton className={styles.accordionButton}>
                      {capitalizeFirstLetter(benchmark)}
                    </AccordionItemButton>
                  </AccordionItemHeading>
                  <AccordionItemPanel className={styles.accordionPanel}>
                    {
                      store.sidebarLinks[benchmark] &&
                      <Accordion
                        allowMultipleExpanded={true}
                        allowZeroExpanded={true}
                        className={`${styles.accordion} ${styles.tierTwo}`}
                        >
                        {
                          Object.keys(store.sidebarLinks[benchmark]).map((ara, j) => {
                            return (
                              <AccordionItem key={j}>
                                <AccordionItemHeading className={styles.accordionHeading}>
                                  <AccordionItemButton className={styles.accordionButton}>
                                    {capitalizeFirstLetter(ara)}
                                  </AccordionItemButton>
                                </AccordionItemHeading>
                                <AccordionItemPanel className={`${styles.accordionPanel} ${styles.checkboxes}`}>
                                  {
                                    store.sidebarLinks[benchmark][ara] && 
                                    Object.entries(store.sidebarLinks[benchmark][ara]).map(([i, timestamp], k) => {
                                      return(
                                        <Checkbox 
                                          key={k}
                                          value={{benchmark, ara, timestamp}}
                                          >
                                            {/* {timestamp.substring(0,10).replaceAll('-', ' ')} */}
                                            {timestamp}
                                        </Checkbox>
                                      );
                                    })
                                  }
                                </AccordionItemPanel>
                              </AccordionItem>
                            );
                          })
                        }
                      </Accordion>  
                    }
                  </AccordionItemPanel>
                </AccordionItem>
              );
            })        
          }
        </Accordion>
      }
    </div>
  )
};

export default Sidebar;